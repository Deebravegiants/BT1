# [H] Nerdbank.MessagePack: Attacker-controlled stackalloc in DateTime decoding causes process-terminating StackOverflowException

## Summary
Severity: High
Advisory: GHSA-2cwq-pwfr-wcw3
CVE: CVE-2026-44375
CWE: CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-2cwq-pwfr-wcw3
Type: github-advisory

## Affected
- NuGet: `Nerdbank.MessagePack` — affected >=0 <1.1.62

## Details
### Summary

Nerdbank.MessagePack contains an uncontrolled stack allocation vulnerability in DateTime decoding. A malicious MessagePack payload can declare an oversized timestamp extension length, causing the reader to allocate an attacker-controlled number of bytes on the stack. This can trigger a `StackOverflowException`, which is not catchable by user code and terminates the process.

### Impact

Applications are impacted if they deserialize MessagePack data from untrusted or attacker-controlled sources using Nerdbank.MessagePack and the target type contains a `DateTime` value.

A small malicious payload can cause process termination, resulting in a denial of service. This may affect services, APIs, workers, message consumers, or other long-running processes that deserialize untrusted MessagePack input.

The issue occurs because DateTime timestamp extension decoding derives `tokenSize` from the attacker-controlled extension length before validating that the timestamp length is one of the legal MessagePack timestamp sizes: 4, 8, or 12 bytes. When the buffer is incomplete, that unvalidated size is propagated to the streaming reader slow path, where it is used in a `stackalloc`.

### Patches

The 1.1.62 version contains the fix for this security vulnerability.

### Workarounds

If upgrading is not yet possible, avoid deserializing untrusted MessagePack payloads into type graphs that may contain `DateTime` fields or properties.

Input byte-size limits alone may not fully mitigate this issue, because the malicious payload can be small while declaring a very large extension length. Possible mitigations include:

- Pre-validating MessagePack extension headers before deserialization and rejecting timestamp extensions whose length is not 4, 8, or 12 bytes.
- Rejecting or filtering extension type `-1` timestamp values from untrusted input unless they are known to be valid.
- Running deserialization of untrusted payloads in an isolated process that can be safely restarted after termination.
- Restricting MessagePack deserialization to trusted producers until a patched version is available.

### Resources

- CWE-789: Uncontrolled Memory Allocation: https://cwe.mitre.org/data/definitions/789.html
- MessagePack timestamp extension specification: https://github.com/msgpack/msgpack/blob/master/spec.md#timestamp-extension-type

## References
- https://github.com/AArnott/Nerdbank.MessagePack/security/advisories/GHSA-2cwq-pwfr-wcw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44375
- https://github.com/AArnott/Nerdbank.MessagePack/pull/941
- https://github.com/AArnott/Nerdbank.MessagePack/commit/7d1eb319cfabe7280e70699946c9a48579fa2f30
- https://github.com/AArnott/Nerdbank.MessagePack
- https://github.com/AArnott/Nerdbank.MessagePack/releases/tag/v1.1.62
- https://github.com/msgpack/msgpack/blob/master/spec.md#timestamp-extension-type
