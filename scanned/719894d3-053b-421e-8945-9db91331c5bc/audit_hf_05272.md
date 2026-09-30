# [H] Uint64 Overflow in Payout Distribution

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23486
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Distribution of payouts will revert due to overflow when payment is made using a stablecoin with high decimals.  
Payouts are meant to be paid using a stablecoin, originally a stablecoin with 6 decimals (USDC). The system can change the stablecoin used for payments, e.g., USDT (8 decimals) or USDS (18 decimals).  

As part of the changes made to introduce the PaymentSettler, the data type of the variable `calculatedPayout` was changed from a `uint256` to a `uint64`. This change introduces a critical vulnerability that can cause an irreversible denial‑of‑service to users trying to collect their payouts.  

A `uint64` would revert when distributing a payout of 20 USD using a stablecoin of 18 decimals because the resulting amount (`20e18`) exceeds the maximum value a `uint64` can hold.  

If a user has multiple pending distributions and the most recent distribution is paid with a stablecoin of 18 decimals (e.g., earning 50 USD on each distribution), attempting to calculate the payout will cause the transaction to revert. The last distribution pushes the payout amount beyond the `uint64` limit, and the safe cast to `uint64` overflows, blocking the user from claiming both the most recent and all previous undistributed payouts.

## Proof of Concept
```solidity
bool a = type(uint64).max > 20e18;
a
// Type: bool
// Value: false
```

```solidity
function payoutBalance(address holder) public returns (uint256) {
    ...
    for (uint16 i = payRangeStart; i >= payRangeEnd; --i) {
        ...
        PayoutInfo memory pInfo = $._payouts[i];
        // @audit => `pInfo.amount` set using a stablecoin with high decimals will bring up the payoutAmount
        // beyond the limit of what can fit in a uint64,!
        payoutAmount +=
            (curEntry.tokenBalance * pInfo.amount) /
            pInfo.totalSupply;
        if (i == 0) break; // to prevent potential overflow
    }
    ...
    if (payoutForwardAddr == address(0)) {
        // @audit-issue => overflow will blow up the tx
        holderStatus.calculatedPayout += SafeCast.toUint64(payoutAmount);
    } else {
        // @audit-issue => overflow will blow up the tx
        $._holderStatus[payoutForwardAddr].calculatedPayout += SafeCast
            .toUint64(payoutAmount);
    }
}
```

## Recommendation
Recommended Mitigation: To solve this issue, the most straightforward fix is to change the data type of `calculatedPayout` to at least `uint128` and consider standardizing all token amounts to `uint128`.  

It is further recommended to normalize the internal accounting of the system to a fixed number of decimals so that it is not affected by the decimals of the actual stablecoin used for payments. As part of this change, the `PaymentSettler` contract must be responsible for converting the values sent and received from the `RemoraToken` to the actual decimals of the currently configured stablecoin.
