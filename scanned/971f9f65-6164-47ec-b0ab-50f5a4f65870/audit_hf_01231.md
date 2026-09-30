# [M] Inﬂation Attack

## Summary
Severity: Medium
Contest weight: 0.4492
Dataset id: 5579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An inflation attack arises from the way the contract calculates shares on the very first mint. The function that converts deposited assets to shares treats the situation where totalShares is less than a constant LOCKED_SHARES as an “initial deposit”. In that branch it subtracts LOCKED_SHARES from the computed share amount, assuming that the caller has already contributed at least that many locked shares. Because the contract does not enforce a minimum asset amount that matches the locked share count, an attacker can deposit LOCKED_SHARES+1 assets. The formula then yields shares equal to the asset amount, and after subtracting LOCKED_SHARES the attacker receives exactly one share while having supplied a huge amount of assets. Consequently the internal accounting now values one share as LOCKED_SHARES+1 assets. Any subsequent user who deposits after this inflated state receives fewer shares than expected, effectively losing part of their contribution to the attacker. The vulnerability is triggered only on the first mint when totalSupply is zero; after the initial share price has been inflated, normal deposits continue to use the distorted price. Users notice the problem as a sudden drop in the number of shares they receive for a given deposit, or as missing refunds when they try to withdraw. The issue was discovered during a manual audit that examined the edge case of the initial deposit logic. It is difficult to spot because the conversion function works correctly for typical deposits and the subtraction of LOCKED_SHARES appears to protect the protocol, masking the fact that an oversized initial deposit can manipulate the share price. To remediate, the contract should either mint the locked shares to an irrecoverable address at deployment, enforce that the first deposit exactly matches the locked share amount, or prevent any subtraction of locked shares on the initial mint. In general, the bug belongs to the class of “initialization‑state arithmetic manipulation” where assumptions about a zero‑state balance are violated, leading to inflation of token value and loss of funds for later participants.

## Proof of Concept
1. User deposits LOCKED_SHARES + 1.
2. convertToShares is called internally. Since this is first mint (totalSupply==0) so initialDeposit is true and depositSharePrice will be FIXED_POINT_SCALE making shares=assets .
```solidity
function convertToShares(
    uint256 assets
) public view nonZeroUint(assets) returns (uint256) {
    /* Check if initial deposit */
    bool initialDeposit = totalShares() < LOCKED_SHARES;
    /* Compute shares */
    uint256 shares = ((assets * FIXED_POINT_SCALE) / depositSharePrice());
    /* Check if initial deposit and shares is less than locked shares */
    if (initialDeposit && shares <= LOCKED_SHARES) revert InvalidAmount();
    /* Compute shares. If initial deposit, lock subset of shares */
    return shares - (initialDeposit ? LOCKED_SHARES : 0);
}
```
3. So value returned would be (LOCKED_SHARES + 1)-LOCKED_SHARES = 1. Thus 1 share get minted to User.
4. So, 1 share is now worth LOCKED_SHARES + 1 assets.
5. Attacker can now front run any victim deposit by large donation, causing victim to get lower than expected shares especially if deposit was made with min amount 0.

## Recommendation
Mint LOCKED_SHARES to say 0xdead address on first mint which makes this attack expensive.
