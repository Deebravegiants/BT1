# [M] s2n-quic has excessive memory allocation

## Summary
Severity: Medium
Advisory: GHSA-9q54-f358-3fqf
CVE: CVE-2026-10740
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-9q54-f358-3fqf
Type: github-advisory

## Affected
- crates.io: `s2n-quic` — affected >=0 <1.82.0

## Details
s2n-quic is a Rust implementation of the QUIC protocol. An unauthenticated user can attempt to exhaust server memory on an s2n-quic endpoint by sending crafted CRYPTO frames with high offsets. The buffer used for processing CRYPTO frames does not enforce a maximum size. In the worst case, a single 1200-byte packet can cause approximately 9.4 MB of allocation. By repeatedly sending such packets, the resulting memory pressure could cause denial of service. No valid handshake is required.

Impacted versions: <= v1.81.0

### Patches
This issue has been addressed in s2n-quic version v1.82.0. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

### Workarounds
There is no workaround that fully mitigates this issue. Upgrading to the patched version is the recommended remediation.

### References
If there are any questions or comments about this advisory, contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/s2n-quic/security/advisories/GHSA-9q54-f358-3fqf
- https://nvd.nist.gov/vuln/detail/CVE-2026-10740
- https://aws.amazon.com/security/security-bulletins/2026-042-aws
- https://github.com/aws/s2n-quic
- https://github.com/aws/s2n-quic/releases/tag/v1.82.0
