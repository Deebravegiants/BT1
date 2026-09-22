# [H] xrdp: Fail-open privilege drop in sesexec — child processes may execute as root if setuid fails

## Summary
Severity: High
Advisory: CVE-2026-32107
Aliases: GHSA-p5m6-7m43-pjv9
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-32107
Type: osv

## Details
xrdp is an open source RDP server. In versions through 0.10.5, the session execution component did not properly handle an error during the privilege drop process. This improper privilege management could allow an authenticated local attacker to escalate privileges to root and execute arbitrary code on the system. An additional exploit would be needed to facilitate this. This issue has been fixed in version 0.10.6.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32107.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-p5m6-7m43-pjv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32107
