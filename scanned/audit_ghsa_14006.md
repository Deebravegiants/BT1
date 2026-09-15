# [H] swift-nio-http2 vulnerable to denial of service via ALTSVC or ORIGIN frames

## Summary
Severity: High
Advisory: GHSA-pgfx-g6rc-8cjv
CVE: CVE-2022-24668
CWE: CWE-241
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-18
Source: https://github.com/advisories/GHSA-pgfx-g6rc-8cjv
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-http2` — affected >=1.0.0 <1.19.2

## Details
A program using swift-nio-http2 is vulnerable to a denial of service attack caused by a network peer sending ALTSVC or ORIGIN frames. This attack affects all swift-nio-http2 versions from 1.0.0 to 1.19.1. It is fixed in 1.19.2 and later releases.

This vulnerability is caused by a logical error after frame parsing but before frame handling. ORIGIN and ALTSVC frames are not currently supported by swift-nio-http2, and should be ignored. However, one code path that encounters them has a deliberate trap instead. This was left behind from the original development process and was never removed.

Sending an ALTSVC or ORIGIN frame does not require any special permission, so any HTTP/2 connection peer may send such a frame. For clients, this means any server to which they connect may launch this attack. For servers, anyone they allow to connect to them may launch such an attack.

The attack is low-effort: it takes very little resources to send one of these frames. The impact on availability is high: receiving the frame immediately crashes the server, dropping all in-flight connections and causing the service to need to restart. It is straightforward for an attacker to repeatedly send these frames, so attackers require very few resources to achieve a substantial denial of service.

The attack does not have any confidentiality or integrity risks in and of itself. This is a controlled, intentional crash. However, sudden process crashes can lead to violations of invariants in services, so it is possible that this attack can be used to trigger an error condition that has confidentiality or integrity risks.

The risk can be mitigated if untrusted peers can be prevented from communicating with the service. This mitigation is not available to many services.

The issue is fixed by rewriting the parsing code to correctly handle the condition. The issue was found by automated fuzzing by oss-fuzz.

## References
- https://github.com/apple/swift-nio-http2/security/advisories/GHSA-pgfx-g6rc-8cjv
- https://nvd.nist.gov/vuln/detail/CVE-2022-24668
- https://github.com/apple/swift-nio-http2/commit/000ca94f9de92c95b9ac85d44600b7b0fe25a3e5
- https://github.com/apple/swift-nio-http2
- https://github.com/apple/swift-nio-http2/releases/tag/1.19.2
