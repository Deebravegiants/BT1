# [M] xrdp: Malformed Confirm Active capability sets cause out-of-bounds reads

## Summary
Severity: Medium
Advisory: CVE-2026-55238
Aliases: GHSA-mg8j-x9rw-9xv3
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-55238
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain a vulnerability concerning the processing of RDP Confirm Active PDU, where during the capability negotiation phase, the parser did not perform sufficient length validation for specific capability sets. A remote, unauthenticated attacker could potentially exploit this flaw by sending a specially crafted RDP packet containing malformed capability data. Due to missing bounds checks, the xrdp process may perform out-of-bounds memory reads, which can result in the termination of the service (Denial of Service). However, since xrdp forks a new process for each connection by default, an out-of-bounds read causing a process crash is unlikely to bring down the entire xrdp service. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55238.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-mg8j-x9rw-9xv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55238
