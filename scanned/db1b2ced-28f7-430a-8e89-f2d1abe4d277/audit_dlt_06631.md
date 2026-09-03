# [M] Denial of Service (DoS) and Gas Grief Attack in Token Redemption Process

## Summary
Severity: Medium
Chain: Smart contract
Component: SeeR-PM
Published: 2024-09-26
Source: https://github.com/hats-finance/SeeR-PM-0x899bc13919880db76edf4ccd72bdfa5dfa666fb7/issues/82
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xa5b4b9894d4e91e80f7a5a9a31763d4a7e23170ca42a7e834d046b8f62023549
**Severity:** medium

**Description:**
**Description**\
An attacker can potentially launch a Denial of Service (DOS) or Gas Griefing attack when a user attempts to redeem their tokens in the current redemption process.

**Attack Scenario**\
When a user redeems their tokens, the contract iterates over the outcomeIndexes to calculate the token balance and then transfers it back from the user to the contract. The vulnerable code section is as follows:

```solidity
        for (uint256 j = 0; j < outcomeIndexes.length; j++) {
            indexSets[j] = 1 << outcomeIndexes[j];
            tokenId = getTokenId(collateralToken, parentCollectionId, conditionId, indexSets[j]);

            // first we need to unwrap the outcome tokens that will be redeemed.
            (IERC20 wrapped1155, bytes memory data) = market.wrappedOutcome(outcomeIndexes[j]);
@>            uint256 amount = wrapped1155.balanceOf(msg.sender);

            wrapped1155.transferFrom(msg.sender, address(this), amount);

```

**Attack Steps:**

1. The victim user intends to redeem their tokens and approves the necessary token allowance.
2. The victim calls the redeem function, which starts the token redemption process.
3. The attacker detects the victim's redemption call and front-runs it by sending a small amount of tokens (1 wei) to the last token in the outcomeIndexes.
4. During the victim’s transaction, the loop proceeds over all the outcomeIndexes. When it reaches the last index, the redemption logic calculates the user’s balance (now altered by the attacker’s 1 wei transfer).
5. The contract then attempts to transfer this altered balance, causing the transaction to revert.


This forces the victim’s transaction to revert, causing wasted gas and preventing the redemption process.


**Impact:**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SeeR-PM-0x899bc13919880db76edf4ccd72bdfa5dfa666fb7/issues/82_
