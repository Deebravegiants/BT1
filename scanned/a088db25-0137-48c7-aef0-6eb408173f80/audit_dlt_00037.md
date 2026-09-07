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
```

_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-qgw7-x3x7-p35x_
