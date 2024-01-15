from flask import Flask, render_template, request, redirect, url_for,session
from web3 import Web3
import json
app = Flask(__name__)
app.secret_key = '45'
w3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
with open("build/contracts/Election.json", "r") as json_file:
    contract_data = json.load(json_file)
    contract_abi = contract_data["abi"]
    contract_address = "0x272Cb632f8cb908D2f89E8D82c2DfC2C20dD8D8e"  
contract = w3.eth.contract(address=contract_address, abi=contract_abi)
@app.route('/')
def home():
    return render_template('front.html');
@app.route('/a')
def index():
    candidates = []
    for i in range(1, contract.functions.candidatesCount().call() + 1):
        candidate = contract.functions.candidates(i).call()
        candidates.append({"id": candidate[0], "name": candidate[1], "voteCount": candidate[2]})

    return render_template('index.html', candidates=candidates)
@app.route('/ec')
def ec():
    return render_template('electioncommision.html')
@app.route('/verify_voter')
def verify_voter():
    return render_template('verify_voter.html')

@app.route('/verify_voter', methods=['POST'])
def verify_voter_id():
    if request.method == 'POST':
        voter_id = int(request.form['voter_id'])

        sender_voter_ids = contract.functions.getVoterIds().call({'from': w3.eth.accounts[0]})

        if voter_id in sender_voter_ids:
            session['voter_id'] = voter_id
            return redirect(url_for('index'))
        else:
            error_message = "Invalid voter ID. Please check your ID and try again."
            return render_template('verify_voter.html', error_message=error_message)

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_voter():
    if request.method == 'POST':
        voter_ids_input = request.form['voter_ids']
        voter_ids = [int(id) for id in voter_ids_input.split(',')]

        try:
            for voter_id in voter_ids:
                contract.functions.registerVoter(voter_id).transact({'from': w3.eth.accounts[0]})
        except Exception as e:
            return f"Error: {e}"
        
        return redirect(url_for('register_voter'))

@app.route('/vote', methods=['POST'])
def vote():
    if request.method == 'POST':
        voter_id = session.get('voter_id')
        if voter_id is None:
            return "Invalid voter ID. Please verify your voter ID first."

        candidate_id = request.form.get('candidate_id')  
        if not candidate_id.isdigit():
            error_message = "Invalid candidate ID. Please enter a valid candidate ID."
            return render_template('verify_voter.html', error_message=error_message)
        
        try:
            candidate_id = int(candidate_id)
            contract.functions.vote(voter_id, candidate_id).transact({'from': w3.eth.accounts[0]})
        except Exception as e:
            error_message = f"Error: {e}"
            return render_template('verify_voter.html', error_message=error_message)

        session.pop('voter_id', None)
        
        return redirect(url_for('verify_voter_id'))

@app.route('/add_candidate_page')
def add_candidate_page():
    return render_template('add_candidate.html')
@app.route('/add_candidate', methods=['GET'])
def add_candidate_form():
    return render_template('add_candidate.html')
@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    if request.method == 'POST':
        new_candidate_name = request.form['new_candidate']
        new_candidate_party = request.form['new_party']  
        try:
            contract.functions.addCandidate(new_candidate_name, new_candidate_party).transact({'from': w3.eth.accounts[0]})
        except Exception as e:
            return f"Error: {e}"
        return redirect(url_for('add_candidate_page'))
    else:
        return "Method Not Allowed"
@app.route('/results')
def results():
    candidates = []
    max_vote_count = 0 
    for i in range(1, contract.functions.candidatesCount().call() + 1):
        candidate_id, candidate_name, candidate_party, vote_count = contract.functions.getCandidate(i).call()
        candidates.append({"id": candidate_id, "name": candidate_name, "party": candidate_party, "voteCount": vote_count})
        if vote_count > max_vote_count:
            max_vote_count = vote_count
            winner_name = candidate_name
        elif vote_count == max_vote_count:
            winner_name = "Tie"

    return render_template('results.html', candidates=candidates, winner_name=winner_name)
if __name__ == '__main__':
    app.run(debug=True)
