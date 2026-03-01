from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Roster
from sqlalchemy import text, func

finder_bp = Blueprint('finder', __name__)

@finder_bp.route('/')
@login_required
def index():
    # Fetch data as of date
    as_of_query = text("SELECT value FROM public.tbl_config WHERE particular = 'ROSTER_DATE'")
    as_of_res = db.session.execute(as_of_query).fetchone()
    data_as_of = as_of_res[0] if as_of_res else "N/A"
    return render_template('finder/index.html', data_as_of=data_as_of)

@finder_bp.route('/search', methods=['POST'])
@login_required
def search():
    fname = request.form.get('fname', '').strip()
    mname = request.form.get('mname', '').strip()
    lname = request.form.get('lname', '').strip()

    full_name_input = f"{fname} {mname} {lname}".strip()
    
    # Using raw SQL for similarity search as it's more straightforward for pg_trgm similarity
    # similarity(concat_ws(' ', first_name, middle_name, last_name), :input)
    
    query = text("""
        SELECT *, similarity(CONCAT_WS(' ', first_name, middle_name, last_name), :full_name) AS similarity_score
        FROM ds.tbl_roster
        WHERE similarity(CONCAT_WS(' ', first_name, middle_name, last_name), :full_name) > 0.3
        ORDER BY similarity_score DESC
        LIMIT 20
    """)
    
    results = db.session.execute(query, {'full_name': full_name_input}).fetchall()
    
    data = []
    for row in results:
        data.append({
            'hh_id': row.hh_id,
            'name': f"{row.first_name} {row.middle_name} {row.last_name}",
            'birthday': str(row.birthday) if row.birthday else '',
            'address': f"BRGY. {row.barangay}, {row.municipality}",
            'client_status': row.client_status,
            'similarity': f"{round(row.similarity_score * 100, 2)}%",
            'hh_set': row.hh_set,
            'prog': row.prog
        })
    
    return jsonify(data)

@finder_bp.route('/roster', methods=['POST'])
@login_required
def roster():
    hh_id = request.form.get('hh_id')
    if not hh_id:
        return jsonify({'success': False, 'message': 'HHID is required'})
    
    roster_members = Roster.query.filter_by(hh_id=hh_id).all()
    
    data = []
    for member in roster_members:
        data.append({
            'entry_id': str(member.entry_id),
            'name': f"{member.first_name} {member.middle_name} {member.last_name}",
            'relation': member.relation_to_hh_head,
            'birthday': str(member.birthday) if member.birthday else '',
            'sex': member.sex,
            'status': member.member_status,
            'grantee': member.grantee
        })
    
    return jsonify({'success': True, 'roster': data})
