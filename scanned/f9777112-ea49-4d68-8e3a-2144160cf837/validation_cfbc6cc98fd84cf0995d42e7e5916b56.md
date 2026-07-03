### Title
Non-Unique Bridge UID Generation Can Cause Permanent Freezing of Bridged Funds - (File: contracts/bridges/SonicChainNativeTokenBridge.sol)

### Summary
`SonicChainNativeTokenBridge.bridgeTokenToL1` generates a `uid` for each Sonic bridge withdrawal using only block-level and call-level parameters. Two calls in the same block with identical `msg.sender`, `recipient`, `amount`, and `tx.gasprice` produce the same `uid`. If the Sonic bridge uses this caller-supplied `uid` as the withdrawal identifier, the second withdrawal shares the same id as the first, and `SonicBridgeReceiver` on L1 will permanently reject the second claim, freezing those tokens.

### Finding Description
The uid is computed as:

```solidity
uint96 uid = uint96(
    uint256(
        keccak256(
            abi.encodePacked(
                block.timestamp, block.number, msg.sender, recipient, amount, tx.gasprice, bridgeReceiver
            )
        )
    ) % type(uint96).max
);
``` [1](#0-0) 

Within a single block, `block.timestamp`, `block.number`, and `bridgeReceiver` are all fixed constants. The uid therefore depends solely on `msg.sender`, `recipient`, `amount`, and `tx.gasprice`. Two calls sharing those four values in the same block produce an identical uid. There is no nonce, counter, or any monotonically increasing value in the hash preimage.

The uid is passed directly to the Sonic bridge:

```solidity
sonicBridge.withdraw(uid, originalToken, amount);
``` [2](#0-1) 

And emitted in the event:

```solidity
emit TokensBridgedToL1(recipient, amount, uid, bridgeReceiver);
``` [3](#0-2) 

On L1, `SonicBridgeReceiver` tracks claims by `withdrawalId` and permanently marks each id as claimed after the first successful claim:

```solidity
if (claimedWithdrawals[withdrawalId]) revert WithdrawalAlreadyClaimed();
claimedWithdrawals[withdrawalId] = true;
``` [4](#0-3) 

If the Sonic bridge assigns the caller-supplied `uid` as the withdrawal id (consistent with the parameter name and the `uint96` type matching the `Withdrawal` event's `id` field in `ISonicBridge`), then two colliding uids result in two on-chain withdrawals sharing the same id. The first L1 claim succeeds; the second is permanently blocked by `WithdrawalAlreadyClaimed`, and the corresponding tokens are frozen in the Sonic bridge forever.

The fallback uid path (triggered when the primary hash produces zero) is even weaker — it drops `amount` and `recipient` from the preimage:

```solidity
uid = uint96(uint256(keccak256(abi.encodePacked(block.number, msg.sender, tx.gasprice, bridgeReceiver))));
``` [5](#0-4) 

### Impact Explanation
If two bridge calls in the same block share a uid and the Sonic bridge records both under that uid, only one withdrawal can ever be claimed on L1. The tokens from the second withdrawal are permanently frozen in the Sonic bridge with no recovery path inside the LRT-rsETH contracts. This constitutes **permanent freezing of funds**.

### Likelihood Explanation
`bridgeTokenToL1` has no role restriction and is callable by any external account directly. [6](#0-5) 

A collision requires two calls in the same block with identical `msg.sender`, `recipient`, `amount`, and `tx.gasprice`. This is realistic for an automated bridger that batches two equal-sized bridge operations in one block, or for any user who submits two identical transactions. Likelihood is **low-to-medium** but the scenario is not contrived.

### Recommendation
Replace the hash-based uid with a contract-level monotonically increasing counter:

```solidity
uint96 private _uidCounter;

// inside bridgeTokenToL1:
uint96 uid = ++_uidCounter;
```

This guarantees global uniqueness across all calls regardless of block context, eliminating the collision surface entirely.

### Proof of Concept
1. Alice calls `bridgeTokenToL1(recipient, 1 ether)` in block N with `tx.gasprice = 10 gwei`.
2. In the same block N, Alice calls `bridgeTokenToL1(recipient, 1 ether)` again with the same gas price (e.g., via a bundle).
3. Both calls compute the same `uid` because all hash inputs (`block.timestamp`, `block.number`, `msg.sender`, `recipient`, `amount`, `tx.gasprice`, `bridgeReceiver`) are identical.
4. Both calls to `sonicBridge.withdraw(uid, token, 1 ether)` succeed on Sonic (if the bridge does not deduplicate by uid at submission time).
5. On L1, `SonicBridgeReceiver.claimAndTransferToVault(uid, ...)` is called for the first withdrawal — succeeds, sets `claimedWithdrawals[uid] = true`.
6. The second claim with the same `uid` reverts with `WithdrawalAlreadyClaimed`. The second 1 ether is permanently frozen.

### Citations

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L73-73)
```text
    function bridgeTokenToL1(address recipient, uint256 amount) external payable override nonReentrant {
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L91-100)
```text
        // Generate a unique UID for this transaction
        uint96 uid = uint96(
            uint256(
                keccak256(
                    abi.encodePacked(
                        block.timestamp, block.number, msg.sender, recipient, amount, tx.gasprice, bridgeReceiver
                    )
                )
            ) % type(uint96).max
        );
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L103-105)
```text
        if (uid == 0) {
            uid = uint96(uint256(keccak256(abi.encodePacked(block.number, msg.sender, tx.gasprice, bridgeReceiver))));
        }
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L115-115)
```text
        sonicBridge.withdraw(uid, originalToken, amount);
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L123-123)
```text
        emit TokensBridgedToL1(recipient, amount, uid, bridgeReceiver);
```

**File:** contracts/bridges/SonicBridgeReceiver.sol (L79-82)
```text
        if (claimedWithdrawals[withdrawalId]) revert WithdrawalAlreadyClaimed();

        // Mark as claimed before external call to prevent reentrancy
        claimedWithdrawals[withdrawalId] = true;
```
