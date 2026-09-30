# [M] M-15 Variable shadowing

## Summary
Severity: Medium
Contest weight: 0.0402
Dataset id: 7992
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a classic case of variable shadowing that occurs in the contract's initialise routine. A function parameter named trustedForwarder is declared with the same identifier as a state variable that stores the address of the authorised forwarder contract. Because Solidity resolves identifiers to the most local scope first, any assignment to trustedForwarder inside the initialise function actually writes to the parameter, not to the persistent storage slot. As a result the state variable never receives the intended value and remains at its default (usually zero). This mismatch is introduced during contract initialisation, so it only manifests after the initialise function has been called, typically when the contract is first deployed behind a proxy. The root cause is the reuse of the exact variable name for both the argument and the storage field, which hides the storage variable from the function body. An attacker can exploit the bug by invoking functions that rely on the trusted forwarder address for access control or meta‑transaction forwarding. Since the stored forwarder address is still zero, calls that expect a valid forwarder may be rejected, silently fail, or be processed by an unintended fallback, potentially allowing unauthorised parties to execute privileged actions or causing legitimate meta‑transactions to be dropped. From a user perspective the symptoms are subtle: users may see that their transactions are not being forwarded, that NFT minting through a relayer returns no token, or that expected callbacks never occur, leading to confusion such as “my mint transaction succeeded but I received no NFT”. The business logic that assumes a non‑zero trusted forwarder for correct accounting is violated, breaking the contract’s trust model. The issue was discovered during a manual code audit that flagged the identical naming of the parameter and the state variable. It can be hard to notice because the compiler does not emit a warning for shadowing, and the initialise function may appear to set the variable correctly when reading the source. The proper remediation is to rename the function argument (for example to _trustedForwarder) and explicitly assign the argument to the storage variable, or to use a distinct naming convention that prevents shadowing. This fixes the logical error and ensures the forwarder address is stored as intended, restoring correct access control and meta‑transaction behaviour.

## Recommendation
We recommend changing the function parameter name to _trustedForwarder.
