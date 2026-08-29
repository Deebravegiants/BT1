# [M] Depositors could lost all their depositted tokens (including the hTokens) if their address is blacklisted in one of all the depositted underlyingTokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-maia
Published: 2023-10-04
Source: https://github.com/code-423n4/2023-09-maia-findings/issues/423
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-09-maia/blob/main/src/BranchBridgeAgent.sol#L447-L448


# Vulnerability details

## Impact
- All user deposited assets, both, hTokens and underlyingTokens are at risk of getting stuck in a BranchPort if the address of the depositor gets blacklisted in one of all the deposited underlyingTokens

## Proof of Concept
The problem is caused by the fact that the redemption process works by sending back all the tokens that were deposited and that tokens can only be sent back to the same address from where they were deposited.

- Users can deposit/bridgeOut multiple tokens at once (underlyingTokens and hTokens) from a Branch to Root. The system has a mechanism to prevent users from losing their tokens in case something fails with the execution of the crosschain message in the Root environment.
    - If something fails with the execution in Root, the users can retry the deposit, and as a last resource, they can retrieve and redeem their deposit from Root and get their tokens back in the Branch where they were deposited.

- When redeeming deposits, the redemption is made atomically, in the sense that it redeems all the tokens that were deposited at once, it doesn't redeem one or two specific tokens, it redeems all of them.    
    - The problem is that the function to redeem the tokens sets the recipient address to be the caller (msg.sender), and the caller is enforced to be only the owner of the depositor (i.e. the account from where the tokens were taken from).
        - The fact that the depositor's address gets blacklisted in one of the underlying tokens should not cause that all the rest of the tokens to get stuck in the BranchPort.

```solidity
function redeemDeposit(uint32 _depositNonce) external override lock {
    //@audit-info => Loads the deposit's information based on the _depositNonce
    // Get storage reference
    Deposit storage deposit = getDeposit[_depositNonce];

    // Check Deposit
    if (deposit.status == STATUS_SUCCESS) revert DepositRedeemUnavailable();
    if (deposit.owner == address(0)) revert DepositRedeemUnavailable();
    if (deposit.owner != msg.sender) revert NotDepositOwner();

    // Zero out owner
    deposit.owner = address(0);

    //@audit-issue => Sending back tokens to the deposit.owner. Depositors can't specify the address where they'd like to receive their tokens
    // Transfer token to depositor / user
    for (uint256 i = 0; i < deposit.tokens.length;) {
        _clearToken(msg.sender, deposit.hTokens[i], deposit.tokens[i], deposit.amounts[i], deposit.deposits[i]);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-maia-findings/issues/423_
