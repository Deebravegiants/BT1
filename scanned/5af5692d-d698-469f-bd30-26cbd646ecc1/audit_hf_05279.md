# [H] Forwarder can befrozen and still receive and claim payouts while frozen

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23513
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an inconsistency in the freeze logic of a token payout forwarding mechanism. When a holder is designated as a payout forwarder, the contract records a frozenIndex that indicates the payout round at which the address was frozen. The payoutBalance function only blocks payouts for addresses whose frozenIndex is zero, meaning they were frozen before any payout was calculated. Consequently, if the forwarder is frozen after it has already participated in at least one payout, the frozenIndex becomes non‑zero and the eligibility check passes, allowing the forwarder to continue receiving and claiming forwarded payouts despite being frozen. This occurs because the claimPayout function does not re‑verify the frozen status, relying solely on payoutBalance, which contains the flawed condition. An attacker can exploit this by first allowing a forwarder to receive a payout, then freezing the address to bypass any compliance or sanction mechanisms, and still claim subsequent distributions. The impact is that funds intended to be blocked by a freeze can still be withdrawn, breaking the protocol’s accounting assumptions and potentially leading to loss of assets or regulatory violations. The bug manifests only after the first payout has been distributed; before any payout, freezing correctly prevents receipt. Users see a discrepancy where a frozen forwarder still shows a positive payout balance and can claim tokens, contrary to the expectation that freezing stops all payouts. The issue was discovered during an audit through unit tests that froze a forwarder before and after a payout and observed differing behaviours. It is hard to notice because the freeze appears to work in the initial state, and the logic error is hidden in the subtle use of frozenIndex. To remediate, the contract should treat any frozen address as ineligible for receiving or claiming payouts regardless of when it was frozen, either by removing the frozenIndex check or by resetting calculated payouts upon freezing, and by adding explicit frozen‑status guards in the claim function. This aligns the implementation with the intended business rule that freezing fully disables payout forwarding and claimability.

## Proof of Concept
```solidity
function test_forwarderFrozenBeforeFirstPayout_noPayoutBalanceWhileFrozen() external {
    address user1 = users[0];
    address forwarder = users[1];
    uint256 amountToMint = 1;
    _whitelistAndMintTokensToUser(user1, amountToMint);
    _whitelistAndMintTokensToUser(forwarder, amountToMint);
    remoraTokenProxy.setPayoutForwardAddress(user1, forwarder);
    // forwarder frozen before first distribution payout
    remoraTokenProxy.freezeHolder(forwarder);
    uint64 payoutDistributionAmount = 100e6;
    _fundPayoutToPaymentSettler(payoutDistributionAmount);
    // user1 must have 0 payout because it is forwarding to `forwarder`
    uint256 user1PayoutBalance = remoraTokenProxy.payoutBalance(user1);
    assertEq(user1PayoutBalance, 0);
    // forwarder is frozen yet so receives no forwarded payout
    uint256 forwarderPayoutBalancePreUnfreeze = remoraTokenProxy.payoutBalance(forwarder);
    assertEq(forwarderPayoutBalancePreUnfreeze, 0);
}
function test_forwarderFrozenAfterFirstPayout_validPayoutBalanceWhileFrozen_claimPayoutWhileFrozen()
external {,!
    _fundPayoutToPaymentSettler(1);
    42
    address user1 = users[0];
    address forwarder = users[1];
    uint256 amountToMint = 1;
    _whitelistAndMintTokensToUser(user1, amountToMint);
    _whitelistAndMintTokensToUser(forwarder, amountToMint);
    remoraTokenProxy.setPayoutForwardAddress(user1, forwarder);
    remoraTokenProxy.freezeHolder(forwarder);
    uint64 payoutDistributionAmount = 100e6;
    _fundPayoutToPaymentSettler(payoutDistributionAmount);
    // user1 must have 0 payout because it is forwarding to `forwarder`
    uint256 user1PayoutBalance = remoraTokenProxy.payoutBalance(user1);
    assertEq(user1PayoutBalance, 0);
    // forwarder is frozen yet still receives forwarded payout
    uint256 forwarderPayoutBalance = remoraTokenProxy.payoutBalance(forwarder);
    assertEq(forwarderPayoutBalance, payoutDistributionAmount/2);
    // forwarder claims all their payout
    vm.prank(forwarder);
    remoraTokenProxy.claimPayout();
    assertEq(stableCoin.balanceOf(forwarder), forwarderPayoutBalance);
}
```

## Recommendation
The mitigation depends on what the protocol wants to happen in this case, and whether it plans to mitigate L-11. If the protocol wants to allow frozen address to also serve as forwarding addresses and have a payout balance, this could be achieved by:

```solidity
function payoutBalance(address holder) public returns (uint256) {
    HolderManagementStorage storage $ = _getHolderManagementStorage();
    HolderStatus memory rHolderStatus = $._holderStatus[holder];
    uint16 currentPayoutIndex = $._currentPayoutIndex;
    + if ((rHolderStatus.isFrozen && rHolderStatus.frozenIndex == 0) && rHolderStatus.calculatedPayout
    > 0) return rHolderStatus.calculatedPayout;,!
    if (
        (!rHolderStatus.isHolder) || //non-holder calling the function
        (rHolderStatus.isFrozen && rHolderStatus.frozenIndex == 0) || //user has been frozen from
        the start, thus no payout,!
        rHolderStatus.lastPayoutIndexCalculated == currentPayoutIndex // user has already been paid
        out up to current payout index,!
    ) return 0;
}
```
