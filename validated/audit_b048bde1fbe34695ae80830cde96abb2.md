Audit Report

## Title
Signature Replay in `allowPushers` Allows Creator to Re-Establish Revoked Delegation Within Deadline Window - (`smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol`)

## Summary

`CompressedOracle.allowPushers` signs over `(chainid, address(this), deadline, pusher, msg.sender)` with no nonce and no used-signature registry. A creator who retains a pusher's consent signature can replay it an unlimited number of times before `deadline` expires, re-establishing `namespaceRemapping[pusher] = creator` immediately after each `revokePusher()` call. The pusher cannot permanently exit the delegation within the deadline window, causing its pushes to be silently redirected to the creator's namespace and leaving the pusher's own namespace with a frozen timestamp.

## Finding Description

`allowPushers` constructs the signed hash as:

```solidity
// CompressedOracle.sol L204-207
bytes32 hash = MessageHashUtils.toEthSignedMessageHash(
    keccak256(abi.encode(block.chainid, address(this), deadline, pusher, msg.sender))
);
require(pusher == ECDSA.recover(hash, signatures[i]));
```

There is no nonce, no `mapping(bytes32 => bool) usedSignatures`, and no single-use mechanism. `_ensureDeadline` only checks `block.timestamp <= deadline` (OracleBase.sol L124-126), so any valid signature remains replayable for the entire deadline window.

`revokePusher` sets `namespaceRemapping[msg.sender] = address(0)` (CompressedOracle.sol L241), but the creator can immediately call `allowPushers` with the identical signature to restore `namespaceRemapping[pusher] = creator`. This cycle repeats until `deadline` expires.

The `fallback` push path reads `namespaceRemapping[msg.sender]` at the top of every call (CompressedOracle.sol L315-316). While the delegation is active, every push from P writes into C's namespace instead of P's own namespace. P's namespace `timestampMs` freezes at its last pre-attack value.

The code comment at L186-191 explicitly acknowledges that a deadline is required to prevent re-delegation after revocation, but a deadline alone only prevents use *after* expiry — it does not prevent repeated use *before* expiry.

## Impact Explanation

- **Oracle namespace corruption**: P's namespace `timestampMs` stops advancing. Any `feedId` encoding `creator = P` returns a stale `refTime`.
- **Bad-price execution / Swap DoS**: A pool whose `IPriceProvider` reads from P's namespace calls `getBidAndAskPrice()`, which internally reads the stale oracle slot. If the provider's staleness gate is loose, the pool executes swaps at an outdated bid/ask (bad-price execution). If the gate is tight, every `swap` call reaches `_getBidAndAskPriceX64` → `catch` → `revert PriceProviderFailed(reason)` (MetricOmmPool.sol L804-813), making the pool's core swap functionality unusable until P's namespace is refreshed — which P cannot achieve while the delegation is being replayed.

This satisfies the "bad-price execution" and "broken core pool functionality" allowed impact criteria.

## Likelihood Explanation

- **Precondition**: Creator C must hold a valid consent signature from P — the normal operational flow when setting up delegation.
- **Trigger**: C saves the signature off-chain and replays it after each `revokePusher()` call — a single automated transaction.
- **No privilege required**: `allowPushers` is a public function; C is an unprivileged user.
- **Repeatability**: The attack is fully repeatable for the entire deadline window (up to the pusher-chosen expiry, e.g., 1 day).
- **Likelihood**: Low-Medium — requires a malicious creator and an automated pusher whose namespace feeds a live pool.

## Recommendation

Add a per-pusher nonce to the signed payload and increment it on each successful `allowPushers` call:

```solidity
mapping(address => uint256) public pusherNonces;

// Inside allowPushers loop:
bytes32 hash = MessageHashUtils.toEthSignedMessageHash(
    keccak256(abi.encode(
        block.chainid, address(this), deadline,
        pusher, msg.sender,
        pusherNonces[pusher]
    ))
);
require(pusher == ECDSA.recover(hash, signatures[i]));
pusherNonces[pusher]++;
namespaceRemapping[pusher] = msg.sender;
```

Each signed consent becomes single-use; replaying the same signature after revocation fails because the nonce has advanced.

## Proof of Concept

```solidity
function test_allowPushers_replay_after_revoke() public {
    uint256 pusherKey = 0xBEEF;
    address pusher  = vm.addr(pusherKey);
    address creator = address(0xC0DE);
    uint256 deadline = block.timestamp + 1 days;

    bytes32 digest = MessageHashUtils.toEthSignedMessageHash(
        keccak256(abi.encode(block.chainid, address(oracle), deadline, pusher, creator))
    );
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(pusherKey, digest);
    bytes memory sig = abi.encodePacked(r, s, v);

    address[] memory pushers = new address[](1);
    pushers[0] = pusher;
    bytes[] memory sigs = new bytes[](1);
    sigs[0] = sig;

    // Step 1: creator establishes delegation
    vm.prank(creator);
    oracle.allowPushers(deadline, pushers, sigs);
    assertEq(oracle.namespaceRemapping(pusher), creator);

    // Step 2: pusher revokes
    vm.prank(pusher);
    oracle.revokePusher();
    assertEq(oracle.namespaceRemapping(pusher), address(0));

    // Step 3: creator replays the SAME signature — re-establishes delegation without new consent
    vm.prank(creator);
    oracle.allowPushers(deadline, pushers, sigs); // no revert
    assertEq(oracle.namespaceRemapping(pusher), creator); // delegation restored
}
```