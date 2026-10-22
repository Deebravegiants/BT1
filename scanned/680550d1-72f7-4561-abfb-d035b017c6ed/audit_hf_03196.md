# [M] exchangeFee can be escaped

## Summary
Severity: Medium
Contest weight: 0.1004
Dataset id: 17772
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Comparing the before and after balance of the swap call for the swapped amount can be exploited to escape the exchangeFee by wrapping the actual swap inside a fake swap. The attacker can reenter with another CardTopupPermit()->_processTopup()->IExchangeProxyexecuteSwapDirect() at L174 to claw back the fee:
1. Swap minAmount with 1inch, inside the 1inch swap at ExchangeProxy.solL174, reenter and HardenedTopupProxy.solCardTopupPermit();
2. The inner swap is the actual amount: 1M; whichshouldpayfor
As a result, the user successfully escaped most of the exchangeFee. User can escape the exchangeFee.

## Recommendation
Consider adding nonReentrant() modifier to all the 3 non-view methods in the HardenedTopupProxy:
• CardTopupPermit();
• CardTopupTrusted();
• CardTopupMPTProof().
