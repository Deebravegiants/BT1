# [M] Attacker can perform griefing for `process`

## Summary
Severity: Medium
Contest weight: 0.6502
Dataset id: 11424
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[PromiseRouter.sol#L226-L262](https://github.com/code-423n4/2022-06-connext/blob/b4532655071566b33c41eac46e75be29b4a381ed/contracts/contracts/core/promise/PromiseRouter.sol#L226-L262)  

`process()` in `PromiseRouter` is used for process stored callback function and anyone calls it gets `callbackFee` and it calls `callback()` function of `callbackAddress`. but attacker set a `callbackAddress` that reverts on `callback()` and cause `process()` caller griefing. attacker can perform this buy front running or complex logic.

## Proof of Concept
This is `process()` code:
```solidity
/**
 * @notice Process stored callback function
 * @param transferId The transferId to process
 */
function process(bytes32 transferId, bytes calldata _message) public nonReentrant {
  // parse out the return data and callback address from message
  bytes32 messageHash = messageHashes[transferId];
  if (messageHash == bytes32(0)) revert PromiseRouter__process_invalidTransferId();

  bytes29 _msg = _message.ref(0).mustBePromiseCallback();
  if (messageHash != _msg.keccak()) revert PromiseRouter__process_invalidMessage();

  // enforce relayer is whitelisted by calling local connext contract
  if (!connext.approvedRelayers(msg.sender)) revert PromiseRouter__process_notApprovedRelayer();

  address callbackAddress = _msg.callbackAddress();

  if (!AddressUpgradeable.isContract(callbackAddress)) revert PromiseRouter__process_notContractCallback();

  uint256 callbackFee = callbackFees[transferId];

  // remove message
  delete messageHashes[transferId];

  // remove callback fees
  callbackFees[transferId] = 0;

  // execute callback
  ICallback(callbackAddress).callback(transferId, _msg.returnSuccess(), _msg.returnData());

  emit CallbackExecuted(transferId, msg.sender);

  // Should transfer the stored relayer fee to the msg.sender
  if (callbackFee > 0) {
    AddressUpgradeable.sendValue(payable(msg.sender), callbackFee);
  }
}
```

As you can see it calls `ICallback(callbackAddress).callback(transferId, _msg.returnSuccess(), _msg.returnData());` and if that call reverts then whole transaction would revert. so attacker can setup `callbackAddress` that revert and the caller of `process()` wouldn’t get any fee and lose gas.

## Recommendation
Change the code so it won’t revert if call to `callbackAddress` reverts.

If the callback would revert, _normally_ it won’t be called.

However, the attacker (griefer) could potentially frontrun the relayer’s callback transaction (which is already submitted / in the mempool) and update the state of their callback contract in such a way to cause this subsequent callback to fail. Why would they do that? Nothing is gained, only losses are incurred on both sides.

This seems like it should be invalid, but it also seems like we should be doing a try/catch on principle though. Perhaps the issue is misrepresented here - it’s not so much an attack vector as it’s ‘best practice’ / QA issue.

~~Let’s de-escalate to QA issue.~~ Confirming, but would be great to get a second look from @LayneHaber on this.

EDIT: Changed my mind, think the risk level is appropriate.

If you change the message, the following check(s) would fail (since the hash is put onchain when the message is propagated by nomad):
```solidity
bytes32 messageHash = messageHashes[transferId];
if (messageHash == bytes32(0)) revert PromiseRouter__process_invalidTransferId();

bytes29 _msg = _message.ref(0).mustBePromiseCallback();
if (messageHash != _msg.keccak()) revert PromiseRouter__process_invalidMessage();
```
An attacker cannot falsify this message because sending messages on the router is restricted via the `onlyConnext` modifier, so I don’t think changing the `callbackAddress` is a valid attack strategy. 

If we extend this concern to any failing `callback`, then any revert would not be executed. In most cases, this would be caught in offchain simulations meaning the relayer would not submit the transaction (and then nobody could process the callback). This means that integrators _must_ handle failures within their code. This is a common practice when writing crosschain handlers (i.e. nomad `handle` should not revert as the message cannot be reprocessed, functions called via `execute` should handle errors unless sending funds to a recovery address is okay, etc.).

Don’t think this qualifies as a value leak, but because it is potentially unprocessable will leave the severity at 2 and move the label to “acknowledged”.

I guess this issue has the same concerns as [M-01 (Issue #220)](https://github.com/code-423n4/2022-06-connext-findings/issues/220). Even if the onus is on the caller of `process` to simulate the call beforehand, it seems likely that the transaction could be front-run and prove to be poor user experience for relayers. 

I don’t think its realistic that relayers would call this function without first simulating the transaction to see if the callback fails, but I guess the bridge user could set the callback address up as a honey pot such that simulated transactions are successful.

It probably makes sense to remove the main culprit of the issue by using a try/catch statement for the `ICallback(callbackAddress).callback(transferId, _msg.returnSuccess(), _msg.returnData());` call.
