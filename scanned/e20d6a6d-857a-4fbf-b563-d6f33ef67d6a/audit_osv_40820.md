# [M] xrdp: Out-of-bounds read in Client Control PDU processing (xrdp_rdp_process_data_control)

## Summary
Severity: Medium
Advisory: CVE-2026-55645
Aliases: GHSA-3m4m-h22g-c7xx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-55645
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain a vulnerability concerning the processing of Client Control PDUs. During the RDP connection sequence, the parser does not perform sufficient length validation before reading specific data fields from the network stream. A remote, unauthenticated attacker could potentially exploit this flaw by sending a specially crafted, truncated Client Control PDU. Due to missing bounds checks, the xrdp process may perform out-of-bounds memory reads, which can result in the termination of the service (Denial of Service). However, since xrdp forks a new process for each connection by default, an out-of-bounds read causing a process crash is unlikely to bring down the entire xrdp service.This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55645.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-3m4m-h22g-c7xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55645
