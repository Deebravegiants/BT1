# [H] Unpenalized remote DoS via malformed P2P tx/block messages

## Summary
Severity: High
Chain: Zcash
Component: zcash/zcash
Published: 2026-07-19
Source: https://github.com/zcash/zcash/security/advisories/GHSA-qgw7-x3x7-p35x
Type: github-advisory

## Details
### Summary
Any remote peer can send malformed P2P `tx` or `block` messages that trigger deserialization failures in shielded transaction components, and the victim node will **never** apply `Misbehaving()` to ban or disconnect the attacker. The `consensus_rule_failure` exception type—explicitly designed in `validation.h` to warrant a 100-point DoS ban—is only caught by the generic `std::ios_base::failure` handler in `ProcessMessages()`, which only pushes a `reject` message and logs the error. Additionally, Sapling v4 and v5 (plus Orchard) parsers throw asymmetric exception types for identical classes of malformed input, so v4 violations are semantically distinguishable but still unpenalized, while v5/Orchard violations are indistinguishable from benign I/O errors and receive the same lenient treatment.

### Impact

This constitutes a high-severity denial-of-service vector. While malformed P2P messages are correctly rejected (a reject response is sent and the event is logged), the implementation never applies the corresponding misbehavior penalty, allowing an attacker to repeatedly transmit invalid payloads without accumulating ban score or triggering disconnection. Although each malformed message is inexpensive to deserialize and reject, the absence of enforcement enables persistent abuse at scale and leaves the node exposed to sustained resource exhaustion attempts. More importantly, this represents a direct violation of the project's documented security policy: validation.h explicitly specifies Misbehaving(pnode, 100) for consensus_rule_failure, yet this penalty is never propagated into the P2P message handlers. The root cause is that the exception type was originally introduced for RPC error propagation (DecodeHexTx), while its documented enforcement path on the P2P layer was never implemented, creating a gap between the intended security model and the actual network behavior.

### Details

**1. The intended DoS policy is documented but unimplemented.**
`src/consensus/validation.h:13-31`
```cpp
/**
 * Exception thrown by deserializers when the input bytes violate a consensus
 * rule ...
 * Callers with peer context (i.e. P2P message handlers) SHOULD catch this
 * specifically and apply `Misbehaving(pnode, 100)`; other parse failures
 * may be handled more leniently.
 */
class consensus_rule_failure : public std::ios_base::failure {
```

**2. `ProcessMessages()` never calls `Misbehaving()` for any parse failure.**
`src/main.cpp:8973-8990`
```cpp
catch (const std::ios_base::failure& e)
{
    pfrom->PushMessage("reject", strCommand, REJECT_MALFORMED, string("error parsing message"));
    if (strstr(e.what(), "end of data")) { /* lenient */ }
    else if (strstr(e.what(), "size too large")) { /* lenient */ }
    else { PrintExceptionContinue(&e, "ProcessMessages()"); }
}
```
There is no `catch (const consensus_rule_failure&)` block, and the generic handler does **not** call `Misbehaving()`. Because `consensus_rule_failure` inherits from `std::ios_base::failure`, it is swallowed by this catch.

**3. The `tx` and `block` message handlers perform deserialization inside `ProcessMessage()` with no local try/catch.**
`src/main.cpp:8429-8440`
```cpp
else if (strCommand == "tx" && !IsInitialBlockDownload(...))
{
    ...
    CTransaction tx;
    vRecv >> tx;   // Deserialization; exceptions propagate to ProcessMessages()
```

`src/main.cpp:8628-8651`
```cpp
else if (strCommand == "block" && !fImporting && !fReindex)
{
    CBlock block;
    vRecv >> block;   // Deserialization; exceptions propagate to ProcessMessages()

    ...
    ProcessNewBlock(state, chainparams, pfrom, &block, forceProcessing, NULL);
    int nDoS;
    if (state.IsInvalid(nDoS)) {
        ...
        if (nDoS > 0) {
            Misbehaving(pfrom->GetId(), nDoS);  // Only for VALIDATION failures, never deserialization failures
        }
    }
```

**4. Asymmetric exception types between v4 Sapling and v5 Sapling / Orchard.**
`src/primitives/sapling.h:139-152`
```cpp
template<typename Stream>
void Unserialize(Stream& s) {
    try {
        inner = sapling::parse_v4_components(...);
    } catch (const std::exception& e) {
        // ... Throw `consensus_rule_failure` so that P2P handlers can distinguish
        // and apply DoS scoring accordingly.
        throw consensus_rule_failure(e.what());
    }
}
```

`src/primitives/sapling.h:75-82`
```cpp
template<typename Stream>
void Unserialize(Stream& s) {
    try {
        inner = sapling::parse_v5_bundle(*ToRustStream(s));
    } catch (const std::exception& e) {
        throw std::ios_base::failure(e.what());
    }
}
```

`src/primitives/orchard.h:77-84`
```cpp
template<typename Stream>
void Unserialize(Stream& s) {
    try {
        inner = orchard_bundle::parse(*ToRustStream(s));
    } catch (const std::exception& e) {
        throw std::ios_base::failure(e.what());
    }
}
```

v4 Sapling wraps all parse errors (including the `valueBalanceSapling` range check) in `consensus_rule_failure`. v5 Sapling and Orchard throw plain `std::ios_base::failure`. Both types reach the same unpenalized catch block in `ProcessMessages()`.

### PoC

**Target:** Any `zcashd` node with an open inbound P2P port (default 8233 mainnet, 18233 testnet, 18444 regtest). The victim must not be in initial block download for the `tx` vector; the `block` vector works regardless of IBD state.

**Attacker setup:** A custom P2P client or a patched `zcashd` peer that can open a TCP connection, perform the version/verack handshake, and send raw `tx` or `block` messages.

**Steps to reproduce the `tx` vector:**

1. Start the victim node with `-debug=net` so `ProcessMessages()` logs are visible.
2. Connect the attacker peer to the victim's P2P port.
3. Send a P2P `tx` message containing a crafted transaction payload. Construct an Overwintered transaction header (`fOverwintered = true`, `nVersionGroupId = 0x892F2085`) with a Sapling v4 bundle containing a `valueBalanceSapling` outside the valid range (e.g., `MAX_MONEY + 1`).
   *Why this works:* `CTransaction::Unserialize` will select the v4 Sapling parsing path. `SaplingV4Reader::Unserialize` calls `sapling::parse_v4_components`, which enforces the `valueBalanceSapling` consensus range check. The Rust parser throws, and the C++ wrapper rethrows it as `consensus_rule_failure`.
4. On the victim, observe `debug.log`. The node logs the caught exception via `PrintExceptionContinue` and sends a `reject` message with `REJECT_MALFORMED`. **Crucially, there is no `Misbehaving` log entry** for the attacker peer.
5. Repeat step 3 from the same peer connection. Because no penalty is applied, the peer is never scored toward a ban or disconnected, so it can keep sending malformed messages on the same connection. Each is deserialized and rejected at modest per-message cost; the practical shortfall is the absence of the intended misbehavior penalty rather than significant resource exhaustion.

**Steps to reproduce the `block` vector:**

1. Send a P2P `block` message where one of the non-coinbase transactions contains a corrupted Orchard bundle (e.g., an invalid action count or truncated proof data).
2. `vRecv >> block` will fail during transaction deserialization inside the block. The exception propagates out of `ProcessMessage()` to `ProcessMessages()`.
3. `ProcessNewBlock()` is never reached, so the `state.IsInvalid(nDoS)` path that normally calls `Misbehaving()` is bypassed entirely. The victim again logs the exception and sends `reject`, but does not ban the peer.

**Steps to reproduce the v5/Orchard asymmetry:**

1. Send a `tx` message with a v5-format transaction containing a Sapling bundle with an invalid spend description encoding, or an Orchard bundle with a non-canonical action `rk`.
2. `SaplingBundle::Unserialize` or `OrchardBundle::Unserialize` throws plain `std::ios_base::failure`.
3. The victim catches it in the same generic handler, treats it identically to the v4 case, and again fails to apply `Misbehaving()`.

### Remediation

Node operators should migrate to [Zebra](https://github.com/ZcashFoundation/zebra) (the replacement consensus node) and [Zallet](https://zcash.github.io/zallet/) (the full-node wallet, which supports the `zcashd` `wallet.dat`).
