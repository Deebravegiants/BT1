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
            excessFeeRefundAddress = AddressAliasHelper.applyL1ToL2Alias(excessFeeRefundAddress);
        }
```

The check for contract/non-contract relies on openzeppelin librarie's `AddressUpgradeable.isContract` function, which inspects `account.code.length`, like this:-
```solidity
 function isContract(address account) internal view returns (bool) {
        // This method relies on extcodesize/address.code.length, which returns 0
        // for contracts in construction, since the code is only stored at the end
        // of the constructor execution.

        return account.code.length > 0;
    }

```

With ERC-7702, EOAs can temporarily delegate contract code. Such EOAs report a non-zero code.length (commonly 23), causing them to be misclassified as contracts. This results in incorrect aliasing of EOAs, sending refunds to an address that no one controls.

All excess funds are therefore permanently lost.


**Impact**

1. Refunds intended for EOAs using ERC-7702 are irrecoverably locked in their aliased L2 address. Only aliases of contracts are accessable, so these funds are permanently lost.
2. **The arbitration workflow currently requires overpayment of fees to ensure retryable ticket execution. The excess (which is a very large amount) refund is at risk.
3. This creates a loss of funds vector for any user with ERC-7702 delegation enabled.

**Severity: High — direct, permanent loss of user funds.**

**Here is the Vunerable code:-**
- In `_requestArbitration` function:-
```solidity
uint256 ticketID = inbox.createRetryableTicket{value: arbitrumFee}(
    homeProxy,
    L2_CALL_VALUE,
    maxSubmissionCost,
@> msg.sender, // excessFeeRefundAddress
    msg.sender, // callValueRefundAddress
    _parameters[0],
    _parameters[1],
    data
);
```
- In `Inbox.createRetryableTicket` function:
```solidity
if (AddressUpgradeable.isContract(excessFeeRefundAddress)) {
    excessFeeRefundAddress = AddressAliasHelper.applyL1ToL2Alias(excessFeeRefundAddress);
}
```
And in `isContract` function from OZ's library:-

```solidity
return account.code.length > 0;
```

**Attack Scenario**\

1. A user configures their EOA with ERC-7702, delegating minimal code (23-byte code length).
2. They call `requestArbitration`, paying the arbitration cost + retryable ticket fee + excess buffer.
3. The refund address (msg.sender) is misclassified as a contract because `code.length > 0`.
4. The Inbox contract applies aliasing, sending refunds to the aliased address of the EOA.
5. No one controls this aliased address (since it is meant only for contracts).

The refund is permanently lost.

**Attachments**

1. **Proof of Concept (PoC) File**

   Will provide it in the comments

2. **Revised Code File (Optional)**
     
- Implement a safer detection mechanism for EOAs when used as refund addresses. Specifically:

     - If `account.code.length == 23` (or matches known ERC-7702 delegation code patterns), treat it as an EOA and skip aliasing.

Document incompatibility with ERC-7702 in the interim to prevent user fund loss.
