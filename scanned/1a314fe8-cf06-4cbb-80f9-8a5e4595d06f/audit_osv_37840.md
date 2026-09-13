# [C] xrdp: Pre-authentication out-of-bounds reads in RDP capability and channel parsers

## Summary
Severity: Critical
Advisory: CVE-2026-33516
Aliases: GHSA-rvh9-9wm3-28c7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-33516
Type: osv

## Details
xrdp is an open source RDP server. Versions through 0.10.5 contain an out-of-bounds read vulnerability during the RDP capability exchange phase. The issue occurs when memory is accessed before validating the remaining buffer length. A remote, unauthenticated attacker can trigger this vulnerability by sending a specially crafted Confirm Active PDU. Successful exploitation could lead to a denial of service (process crash) or potential disclosure of sensitive information from the process memory. This issue has been fixed in version 0.10.6.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33516.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-rvh9-9wm3-28c7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33516
