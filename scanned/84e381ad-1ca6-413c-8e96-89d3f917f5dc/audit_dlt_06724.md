# [M] Loss of Funds Due to Refund Aliasing in Retryable Ticket Creation

## Summary
Severity: Medium
Chain: Smart contract
Component: Cross-chain-Realitio-Proxy
Published: 2025-09-23
Source: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/7
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/lirezArAzAvi)

  **Beneficiary:** 0xc78291f079Ffe14795E73a4119F0Af631cbC55E2
  **Submission hash (on-chain):** 0xa256e72b0a64e4234a606f15c45704169d2e37d51a62f9fab464cbafe74f4d8c
  **Severity:** medium
  
  **Description:**
  **Description**\
In the `_requestArbitration` function, the `excessFeeRefundAddress` is set to `msg.sender`. While this may work if the caller is an EOA (Externally Owned Account), if the caller is a contract that does not exist on the L2 chain (only on L1), refunds sent to this address will be lost.  

This is because Arbitrum applies an **aliasing mechanism** for addresses coming from L1 → L2 retryables. If the refund address corresponds to an L1 contract that has no L2 deployment, the funds cannot be recovered.

```solidity
uint256 ticketID = inbox.createRetryableTicket{value: arbitrumFee}(
            homeProxy,
            L2_CALL_VALUE,
            maxSubmissionCost,
@>            msg.sender, // excessFeeRefundAddress @audit refund address doesn't exist on L2 if msg.sender is a Contract
            msg.sender, // callValueRefundAddress
            _parameters[0], // l2GasLimit
            _parameters[1], // gasPriceBid
            data
        );
```

- The excess submission fee is refunded to the address on L2 of the `excessFeeRefundAddress` provided when calling `createRetryableTicket` (now if the msg.sender is a contract, the corresponding address doesn't exist on L2, so the excess submission fees will be lost).

- If the retryable auto-redeem fails, the refund will be sent to the aliased address.  
If that address has no contract deployed on L2 (e.g., an L1-only contract), the fund will be permanently lost.

Note: The same may happen everywhere the `createRetryableTicket` is used and `excessFeeRefundAddress` is set to `msg.sender`.
**Attack Scenario**\
- Contract-A requests a new arbitration
- Reality will be notified and a new dispute will be created
- The excess fees should be refunded to `excessFeeRefundAddress` which is Contract-A
- Contract address doesn't exist on L2 -> the funds lost

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/7_
