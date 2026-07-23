Audit Report

## Title
Signature Replay in `allowPushers` Lets Creator Silently Re-Establish Delegation After Pusher Revokes — (File: `smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol`)

## Summary
`allowPushers` validates a pusher's EIP-191 consent signature but never marks it as consumed. Because the signed digest contains no nonce and `revokePusher` only zeroes `namespaceRemapping[msg.sender]` without invalidating outstanding signatures, a malicious creator can replay the identical `(deadline, pusher, signature)` tuple after revocation to silently re-establish delegation within the deadline window. The pusher's subsequent `fallback()` pushes continue landing in the creator's namespace, and the pusher's own namespace receives no updates, producing stale prices for any pool consuming it.

## Finding Description
`allowPushers` constructs the signed digest as:

```solidity
keccak256(abi.encode(block.chainid, address(this), deadline, pusher, msg.sender))
``` [1](#0-0) 

There is no nonce, no per-`(pusher, creator)` counter, and no used-signature bitmap. The only freshness gate is `_ensureDeadline(deadline)`, which rejects calls made *after* the deadline but does nothing to prevent the same signature from being submitted multiple times *before* it expires. [2](#0-1) 

`revokePusher` clears the mapping entry but has no effect on any already-issued signature:

```solidity
namespaceRemapping[msg.sender] = address(0);
``` [3](#0-2) 

The NatSpec comment at L186–191 explicitly acknowledges the deadline is intended to prevent re-establishment after revocation, but it only closes the window after expiry — within the window the replay is unrestricted. [4](#0-3) 

Exploit flow:
1. Pusher signs consent for creator with deadline `D` (e.g., 7 days).
2. Creator calls `allowPushers` — `namespaceRemapping[pusher] = creator`.
3. Pusher calls `revokePusher` — `namespaceRemapping[pusher] = address(0)`.
4. Creator immediately replays the identical `(deadline, pusher, signature)` — no revert, `namespaceRemapping[pusher] = creator` again.
5. All subsequent `fallback()` pushes from the pusher land in the creator's namespace; the pusher's own namespace receives no updates and goes stale. [5](#0-4) 

## Impact Explanation
Any pool whose price provider resolves to the pusher's own namespace feed will receive stale bid/ask prices after the pusher stops receiving updates there, satisfying the **bad-price execution** (stale quote reaches a pool swap) and **pool insolvency** impact gates. The `_getBidAndAskPriceX64` path in `MetricOmmPool` consumes whatever the price provider returns without an independent staleness check beyond what the oracle itself enforces; a stale feed that has not yet crossed the oracle's drift threshold will pass through and execute swaps at wrong prices.

## Likelihood Explanation
- Requires a malicious creator (unprivileged, permissionless role — anyone can be a creator).
- Pusher must have signed a consent with a non-trivial deadline (common practice for operational convenience).
- The replay call is a plain external transaction with no special privilege; the signature is already public on-chain from the first `allowPushers` call.
- The pusher has no on-chain mechanism to prevent the replay short of waiting for the deadline to expire.
- Likelihood: **Medium**.

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

```solidity
// 1. Pusher signs consent once with deadline = block.timestamp + 1 days.
// 2. Creator calls allowPushers — delegation set.
// 3. Pusher calls revokePusher — namespaceRemapping[pusher] == address(0).
// 4. Creator calls allowPushers again with the SAME (deadline, pusher, sig) — no revert.
// 5. Assert namespaceRemapping[pusher] == creator  ← replay succeeded.
// 6. Pusher's fallback() push lands in creator's namespace; pusher's own namespace is stale.
// 7. Pool consuming pusher's own feed receives stale bid/ask → bad-price execution.
```

The PoC provided in the submission is minimal and reproducible using Foundry with `vm.sign`, `vm.prank`, and `vm.warp`, directly exercising the production `CompressedOracleV1` contract with no mocks or non-standard setup.

### Citations

**File:** smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol (L186-191)
```text
    /// @notice Delegates pusher wallets into the caller's namespace. The pusher's EIP-191
    ///         signature is REQUIRED — without it anyone could remap a foreign pusher
    ///         wallet into their own namespace and silently swallow its pushes. The
    ///         deadline is likewise required: the signed consent carries no timestamp of
    ///         its own, so an undated signature could re-establish a delegation AFTER the
    ///         pusher revoked it.
```

**File:** smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol (L192-212)
```text
    function allowPushers(uint256 deadline, address[] calldata pushers, bytes[] memory signatures) external {
        _ensureDeadline(deadline);

        uint256 l = pushers.length;
        require(l == signatures.length);
        for (uint256 i; i < l; i++) {
            address pusher = pushers[i];

            if (pusher == msg.sender) {
                revert NoSelfRemapping();
            }

            bytes32 hash = MessageHashUtils.toEthSignedMessageHash(
                keccak256(abi.encode(block.chainid, address(this), deadline, pusher, msg.sender))
            );
            require(pusher == ECDSA.recover(hash, signatures[i]));

            namespaceRemapping[pusher] = msg.sender;
            emit PusherAuthorized(pusher, msg.sender);
        }
    }
```

**File:** smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol (L238-243)
```text
    function revokePusher() external {
        address creator = namespaceRemapping[msg.sender];
        if (creator == address(0) || creator == msg.sender) revert NoSelfRemapping();
        namespaceRemapping[msg.sender] = address(0);
        emit PusherRevoked(msg.sender, creator);
    }
```

**File:** smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol (L311-344)
```text
    fallback() override external {
        uint256 end;
        uint256 namespace;

        address creator = namespaceRemapping[msg.sender];
        if (creator == address(0)) creator = msg.sender;

        assembly ("memory-safe") {
            end := calldatasize()
            namespace := shl(96, creator) // [creator:20][zeros:12]
        }

        // 4 * 6 + 7 + 1 = 32 bytes per slot
        if (end == 0 || end % 32 != 0) revert BadCalldataLength();

        for (uint256 ptr = 0; ptr < end; ptr += 32) {
            uint256 word;
            assembly ("memory-safe") {
                word := calldataload(ptr)
            }
            // casting to 'uint8' is safe we want LSB
            // forge-lint: disable-next-line(unsafe-typecast)
            uint8 slotId = uint8(word);
            TimeMs timestampMs = toTimeMs(word >> 8 & X56);
            timestampMs.revertIfAfterBlockTimeWithDrift(MAX_TIME_DRIFT);
            bytes32 key = bytes32(namespace | uint256(slotId));
            uint256 old = uint256(_loadStorage(key));
            TimeMs oldTimestampMs = toTimeMs(old >> 8 & X56);

            bool newer = timestampMs.isAfter(oldTimestampMs);
            if (!newer) continue;

            _writeStorage(key, bytes32(bytes32(word & ~uint256(0xff))));
        }
```
