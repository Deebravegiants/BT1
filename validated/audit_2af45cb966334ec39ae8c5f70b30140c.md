The code confirms the claim. Let me verify the key facts:

1. `allowPushers` at line 204-206 constructs the hash with no nonce and no used-signature tracking.
2. `revokePusher` at line 241 only zeroes `namespaceRemapping[msg.sender]` — no signature invalidation.
3. Within the deadline window, the same `(deadline, pusher, signature)` tuple passes `_ensureDeadline` and `ECDSA.recover` every time.
4. The replay restores `namespaceRemapping[pusher] = creator` silently.

The PoC is mechanically sound against the actual code. The pusher's `fallback()` pushes route via `namespaceRemapping[msg.sender]` (line 315-316), so after the replay the pusher's data lands in the creator's namespace — data the pusher no longer intends to provide to that creator. Pools consuming that creator's feed via `IPriceProvider → _getBidAndAskPriceX64` receive those prices.

---

Audit Report

## Title
Signature Replay in `allowPushers` Lets Creator Silently Re-Establish Delegation After Pusher Revokes — (File: `smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol`)

## Summary
`allowPushers` validates a pusher's EIP-191 consent signature but never marks it consumed. Because `revokePusher` only zeroes `namespaceRemapping[msg.sender]` without invalidating outstanding signatures, a malicious creator can replay the identical `(deadline, pushers, signatures)` tuple immediately after revocation, silently restoring delegation. The pusher's subsequent `fallback()` pushes continue to land in the creator's namespace, feeding price data the pusher no longer intends to provide to that creator into pools that consume the creator's oracle feed.

## Finding Description
`allowPushers` constructs the signed digest as:

```solidity
bytes32 hash = MessageHashUtils.toEthSignedMessageHash(
    keccak256(abi.encode(block.chainid, address(this), deadline, pusher, msg.sender))
);
```

There is no nonce, no per-`(pusher, creator)` counter, and no used-signature bitmap. The only freshness gate is `_ensureDeadline(deadline)`, which rejects calls made *after* the deadline but does nothing to prevent the same signature from being submitted multiple times *before* it.

`revokePusher` clears the mapping:

```solidity
namespaceRemapping[msg.sender] = address(0);
```

It has no effect on the already-issued signature. The creator immediately calls `allowPushers` again with the identical tuple; `ECDSA.recover` returns the pusher's address, the `require` passes, and `namespaceRemapping[pusher]` is restored to `msg.sender`. The pusher's revocation is silently undone.

The `fallback()` push path resolves the target namespace via:

```solidity
address creator = namespaceRemapping[msg.sender];
if (creator == address(0)) creator = msg.sender;
```

So every subsequent push from the pusher lands in the creator's namespace, not the pusher's own namespace. The NatSpec comment acknowledges the replay risk but incorrectly claims the deadline fully mitigates it — the deadline only closes the window after expiry; within the window the replay is unrestricted.

## Impact Explanation
`CompressedOracleV1` is the price-delivery layer consumed by `IPriceProvider → MetricOmmPool._getBidAndAskPriceX64`. After the replay, the pusher's `fallback()` pushes update the creator's oracle slots with price data the pusher no longer intends to provide to that creator. If the pusher has revoked in order to stop serving that creator (e.g., to serve a different namespace or asset pair), the creator's feed receives data for the wrong asset or stale/incorrect prices. Pools bound to the creator's price provider execute swaps against those bid/ask values, satisfying the **bad-price execution** impact gate. A pusher who revokes and begins pushing data for a different asset will directly corrupt the creator's feed, causing swaps to execute at wrong prices and exposing traders to principal loss.

## Likelihood Explanation
- The pusher must have signed a consent with a non-trivial deadline (common practice for operational convenience).
- The creator must be malicious or compromised — no special privilege beyond being the `msg.sender` creator is required.
- The replay call is a plain external transaction using a publicly observable signature (emitted or submitted on-chain during the original `allowPushers` call).
- The pusher has no on-chain mechanism to detect or prevent the replay short of waiting for the deadline to expire.

Likelihood: **Medium**.

## Recommendation
Add a per-`(pusher, creator)` nonce to the signed digest and increment it on every successful `allowPushers` call:

```solidity
mapping(address pusher => mapping(address creator => uint256)) public nonces;

bytes32 hash = MessageHashUtils.toEthSignedMessageHash(
    keccak256(abi.encode(
        block.chainid,
        address(this),
        deadline,
        pusher,
        msg.sender,
        nonces[pusher][msg.sender]++
    ))
);
```

After `revokePusher`, the nonce is already incremented, so the old signature is permanently invalid even if the deadline has not expired.

## Proof of Concept
1. Deploy `CompressedOracleV1`.
2. Pusher signs consent once for creator with `deadline = block.timestamp + 1 days`.
3. Creator calls `allowPushers(deadline, [pusher], [sig])` → `namespaceRemapping[pusher] == creator`.
4. Pusher calls `revokePusher()` → `namespaceRemapping[pusher] == address(0)`.
5. Creator calls `allowPushers(deadline, [pusher], [sig])` again with the **identical** arguments — no revert, `namespaceRemapping[pusher] == creator` restored.
6. Pusher's next `fallback()` call routes into the creator's namespace; `oracle.getOracleData(oracle.feedIdOf(creator, slotId, positionId)).price > 0` confirms the creator's feed is updated with the pusher's post-revocation data.