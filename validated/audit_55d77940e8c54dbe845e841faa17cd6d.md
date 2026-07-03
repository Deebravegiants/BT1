### Title
Deterministic UID Collision in `SonicChainNativeTokenBridge.bridgeTokenToL1` Can Permanently Block Bridge Withdrawals - (File: contracts/bridges/SonicChainNativeTokenBridge.sol)

---

### Summary

`SonicChainNativeTokenBridge.bridgeTokenToL1` generates a `uint96` UID from entirely deterministic, block-scoped inputs. Two calls in the same block sharing the same `msg.sender`, `recipient`, `amount`, and `tx.gasprice` produce an identical UID. Because the Sonic bridge's `withdraw` function treats the UID as a unique withdrawal identifier, the second call will be rejected by the bridge, causing the bridge operation to fail.

---

### Finding Description

In `bridgeTokenToL1`, the UID passed to `sonicBridge.withdraw` is computed as:

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

Every input is either a block-level constant (`block.timestamp`, `block.number`) or a call parameter. When the pool contract (e.g. `RSETHPoolV3WithNativeChainBridge`) calls `bridgeTokenToL1` twice in the same block with the same `recipient` (always the L1Vault) and the same `amount`, `msg.sender` (the pool) and `tx.gasprice` are also identical, so the UID is identical for both calls.

The `ISonicBridge` interface documents the first argument to `withdraw` as **"Unique identifier for the withdrawal"**:

```solidity
function withdraw(uint96 uid, address token, uint256 amount) external;
``` [2](#0-1) 

The Sonic bridge is expected to enforce UID uniqueness (otherwise the field serves no purpose). A duplicate UID will therefore cause the second `sonicBridge.withdraw` call to revert.

There is also a fallback UID path that uses an even smaller entropy set (`block.number`, `msg.sender`, `tx.gasprice`, `bridgeReceiver` only), making same-block collisions trivially reproducible whenever the primary hash happens to be zero: [3](#0-2) 

---

### Impact Explanation

When the UID collides, `sonicBridge.withdraw` reverts, which reverts the entire `bridgeTokenToL1` transaction (including the `safeTransferFrom`). The tokens are returned to the caller, but the bridge operation is silently dropped. The pool's `moveAssetsToBridge` call fails, meaning the collected user funds are not forwarded to L1 in that block. Operators must retry in a later block, temporarily freezing the assets inside the L2 pool and delaying the restaking lifecycle for all affected users.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

The pool contract (`RSETHPoolV3WithNativeChainBridge` or similar) is the `msg.sender` for every `bridgeTokenToL1` call. The `recipient` is always the L1Vault address. On Sonic (an EVM-compatible L2), `tx.gasprice` is typically a fixed base fee, making it identical across transactions in the same block. Any two `moveAssetsToBridge` calls in the same block that happen to bridge the same token amount will collide. This is a realistic operational scenario (e.g., a bridger script that batches two bridge calls in one block, or two independent bridger transactions with the same amount landing in the same block).

**Likelihood: Medium.**

---

### Recommendation

Replace the block-scoped hash with a contract-owned monotonically increasing counter (nonce) that is incremented on every call:

```solidity
uint96 private _bridgeNonce;

// inside bridgeTokenToL1:
uint96 uid = ++_bridgeNonce;
```

This guarantees global uniqueness across all calls regardless of block timing, amount, or gas price, directly mirroring the fix recommended in the reference report (use a per-entity counter rather than a shared block-level value).

---

### Proof of Concept

1. Bridger calls `RSETHPoolV3WithNativeChainBridge.moveAssetsToBridge(token, amount)` → internally calls `SonicChainNativeTokenBridge.bridgeTokenToL1(L1Vault, amount)` in block N. UID = `H(ts_N, N, pool, L1Vault, amount, gasprice, receiver)`. `sonicBridge.withdraw(uid, ...)` succeeds.

2. In the same block N, bridger (or a second bridger transaction) calls `moveAssetsToBridge(token, amount)` again with the same `amount` and same `tx.gasprice`. UID = same hash → same `uid`.

3. `sonicBridge.withdraw(uid, ...)` reverts because the UID was already registered.

4. The entire second transaction reverts. The second batch of user funds is not bridged to L1 in block N. Operators must wait for the next block and retry, temporarily freezing those funds in the L2 pool. [4](#0-3)

### Citations

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L91-115)
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

        // Ensure UID is not zero
        if (uid == 0) {
            uid = uint96(uint256(keccak256(abi.encodePacked(block.number, msg.sender, tx.gasprice, bridgeReceiver))));
        }

        // Store the current token balance before withdrawal
        uint256 balanceBefore = token.balanceOf(address(this));

        // Approve the Sonic bridge to spend the tokens
        token.safeIncreaseAllowance(address(sonicBridge), amount);

        // Initiate withdrawal on Sonic bridge
        // Note: Sonic gateway will only allow SonicBridgeReceiver to claim (same address as this contract)
        sonicBridge.withdraw(uid, originalToken, amount);
```

**File:** contracts/interfaces/L2/ISonicBridge.sol (L13-14)
```text
    /// @param amount The amount to withdraw
    function withdraw(uint96 uid, address token, uint256 amount) external;
```
