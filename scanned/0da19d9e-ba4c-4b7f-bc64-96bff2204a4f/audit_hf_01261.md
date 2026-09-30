# [H] offboard() clears all nonces

## Summary
Severity: High
Contest weight: 0.1884
Dataset id: 5787
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function offboard() deletes orgs[msg.sender], which also deletes packedPayoutNonces[].
If the same safe would ever onboard(), with (more or less) the same approvers, then all previous transactions could be re-executed because all the nonces are reset. This could drain the safe.
struct ORG {
    uint128 approverCount;
    uint128 approvalsRequired;
    mapping(address => address) approvers;
    uint256[] packedPayoutNonces;
}
mapping(address => ORG) public orgs;
function offboard() external {
    ...
    delete orgs[msg.sender]; // also deletes packedPayoutNonces
    ...
}

## Recommendation
Apply one of the following solutions:
• use separate contracts for each gnosis safe (see the issue with that name) and deploy a new contract for a new onboard();
• clear the data but set a flag to prevent onboard() again;
• don't clear the packedPayoutNonces[] and allow onboard() again;
• clear the data but keep an onboard nonce which is increased on every onboard and includes that in the signature via validatePayrollTxHashes().
