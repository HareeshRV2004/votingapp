// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Election {
    // Model a Voter
    struct Voter {
        uint[] voterIds; // Store multiple voter IDs for each voter
        mapping(uint => bool) hasVoted; // Track votes for each voter ID
    }

    // Store voters and their voter IDs
    mapping(address => Voter) private voters;

    // Model a Candidate
    struct Candidate {
        uint id;
        string name;
        string party; // Party name
        uint voteCount;
    }

    // Store candidates
    mapping(uint => Candidate) public candidates;
    uint public candidatesCount;

    // Constructor
    constructor() {
        addCandidate("Ranjit", "Congress");
        addCandidate("Sharan", "Bjp");
        addCandidate("sanjith", "PMK");
    }

    // Add a candidate with name and party
    function addCandidate(string memory _name, string memory _party) public {
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, _party, 0);
    }

    // Register a voter with a voter ID
    function registerVoter(uint _voterId) public {
        require(_voterId > 0, "Invalid voter ID.");

        // If the voter has not registered yet, initialize their voter struct
        if (voters[msg.sender].voterIds.length == 0) {
            voters[msg.sender].voterIds.push(_voterId);
        } else {
            // Check if the voter ID is already registered for this address
            for (uint i = 0; i < voters[msg.sender].voterIds.length; i++) {
                require(voters[msg.sender].voterIds[i] != _voterId, "You have already registered this voter ID.");
            }

            // Add the new voter ID to the sender's list of voter IDs
            voters[msg.sender].voterIds.push(_voterId);
        }
    }

    // Vote for a candidate using a specific voter ID
    function vote(uint _voterId, uint _candidateId) public {
        require(voters[msg.sender].voterIds.length > 0, "You are not registered.");
        require(_voterId > 0, "Invalid voter ID.");
        require(!voters[msg.sender].hasVoted[_voterId], "You have already voted with this voter ID.");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate.");

        // Record that the sender has voted with the specified voter ID
        voters[msg.sender].hasVoted[_voterId] = true;

        // Update candidate vote count
        candidates[_candidateId].voteCount++;
    }

    // Get the list of voter IDs for the sender
    function getVoterIds() public view returns (uint[] memory) {
        return voters[msg.sender].voterIds;
    }

    // Get the number of candidates
    function getCandidatesCount() public view returns (uint) {
        return candidatesCount;
    }

    // Get candidate information by ID
    function getCandidate(uint _candidateId) public view returns (uint, string memory, string memory, uint) {
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate.");
        Candidate memory candidate = candidates[_candidateId];
        return (candidate.id, candidate.name, candidate.party, candidate.voteCount);
    }
}
