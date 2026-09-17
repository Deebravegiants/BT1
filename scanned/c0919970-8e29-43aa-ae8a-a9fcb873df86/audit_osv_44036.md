# [M] CVE-2026-78135

## Summary
Severity: Medium
Advisory: CVE-2026-78135
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-78135
Type: osv

## Details
libcharon in strongSwan 5.9.7 through 6.0.7 mishandles behavioral workflow in the IKEv2 state machine. Because CREATE_CHILD_SA requests are mishandled, there can be an authentication bypass.

## References
- https://github.com/strongswan/strongswan/releases/tag/6.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78135.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78135
- https://www.strongswan.org/blog/2026/09/07/strongswan-vulnerability-(cve-2026-78135).html
