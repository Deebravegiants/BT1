# [H] The `requestArbitration` function of arbitrum foreign proxy doesn't handle ERC-7702 enabled EOAs, this leads to complete loss of funds

## Summary
Severity: High
Chain: Smart contract
Component: Cross-chain-Realitio-Proxy
Published: 2025-09-25
Source: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/47
Type: hats-finding

## Details
**Github username:** @Aasifusmani1552
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Aasif)

  **Beneficiary:** 0xF3234DE4984837e01E6489acfc9eD8834A8B4CE3
  **Submission hash (on-chain):** 0xf44f9cb2552350adfbd96ac7ca735aa97983f0d24b23bd842d863f92339b3b53
  **Severity:** high
  
  **Description:**
  **Description**\

The `requestArbitration` function in `RealitioForeignProxyArbitrum` forwards user funds through an Arbitrum retryable ticket. It sets `msg.sender` as the `excessFeeRefundAddress` when creating the ticket.

**Due to Arbitrum’s aliasing rules, if the refund address is a contract, it is rewritten to its L2 alias**, can be checked here in `createRetryableTicket` function:-

```solidity
 function createRetryableTicket(
        address to,
        uint256 l2CallValue,
        uint256 maxSubmissionCost,
        address excessFeeRefundAddress,
        address callValueRefundAddress,
        uint256 gasLimit,
        uint256 maxFeePerGas,
        bytes calldata data
    ) external payable whenNotPaused onlyAllowed returns (uint256) {
        // ensure the user's deposit alone will make submission succeed
        if (msg.value < (maxSubmissionCost + l2CallValue + gasLimit * maxFeePerGas)) {
            revert InsufficientValue(
                maxSubmissionCost + l2CallValue + gasLimit * maxFeePerGas,
                msg.value
            );
        }

        // if a refund address is a contract, we apply the alias to it
        // so that it can access its funds on the L2
        // since the beneficiary and other refund addresses don't get rewritten by arb-os
**@>**        if (AddressUpgradeable.isContract(excessFeeRefundAddress)) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/47_
