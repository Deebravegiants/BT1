# [M] In `BondingCurveFundingManagerBase` consider `minBuyAmount`, because user can buy dust amounts to skip paying fee

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-05
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/22
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xccb3e2a9153e101eb53368556d2586017ad37c9f057d5a99dfc90913e4d4d1fd
**Severity:** medium

**Description:**
**Description**\
If a orchestrator owner has set a fee of 2%(200) for his `BondingCurveFundingManagerBase`, one could bypass it if he repeatedly calls `buy` with an amount of `49` (which is equal 9800) and will round to 0 for the fee calculation in the following part. 

```
    function _calculateNetAmountAndFee(uint _transactionAmount, uint _feePct)
        internal
        pure
        returns (uint netAmount, uint feeAmount)
    {
        // Calculate fee amount
        feeAmount = (_transactionAmount * _feePct) / BPS;
        // Calculate net amount after fee deduction
        netAmount = _transactionAmount - feeAmount;
    }
```

This may seem neglectable, but there could be cases, when it is beneficial for the exploiter. If the protocol is deployed on a L2 chain and the activity is low, one has to pay ~ $0, so he could construct a loop script to buy tokens without paying fee.
**Attack Scenario**\
Describe how the vulnerability can be exploited.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
Implement `minBuyAmount` state variable, which would be modified by the owner of the module.
