# [M] No max for advanceIncentive

## Summary
Severity: Medium
Contest weight: 0.1415
Dataset id: 1138
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function setAdvanceIncentive of DAO.sol doesn’t check for a maximum value of incentive. If incentive would be very large, then advanceIncentive would be very large and the function advance() would mint a large amount of malt.

The function setAdvanceIncentive() can only be called by an admin, but a mistake could be made. Also if an admin would want to do a rug pull, this would be an ideal place to do it.

## Proof of Concept
function setAdvanceIncentive(uint256 incentive) external onlyRole(ADMIN_ROLE, "Must have admin role") {
    ...
    advanceIncentive = incentive;

function advance() external {
    ...
    malt.mint(msg.sender, advanceIncentive * 1e18);

## Recommendation
Check for a reasonable maximum value in advance()

Definitely need to guard against arbitrarily large incentives. Disagree the risk is medium though.

Agree with the finding, this is an example of admin privilege, where the admin can set a variable which can be used to dilute the token and rug the protocol.

Because this is contingent on the admin’s action, I believe medium severity to be proper

The simple rationale on the medium severity is that the owner could set the incentive to an exorbitant amount with the goal of minting a lot of tokens for an exit scam
