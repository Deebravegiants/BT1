# [M] Improper Authorization in github.com/fleetdm/fleet

## Summary
Severity: Medium
Advisory: CVE-2022-24841
Aliases: GHSA-pr2g-j78h-84cr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2022-24841
Type: osv

## Details
fleetdm/fleet is an open source device management, built on osquery. All versions of fleet making use of the teams feature are affected by this authorization bypass issue. Fleet instances without teams, or with teams but without restricted team accounts are not affected. In affected versions a team admin can erroneously add themselves as admin, maintainer or observer on other teams. Users are advised to upgrade to version 4.13. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24841.json
- https://github.com/fleetdm/fleet/security/advisories/GHSA-pr2g-j78h-84cr
- https://nvd.nist.gov/vuln/detail/CVE-2022-24841
- https://github.com/fleetdm/fleet/commit/da171d3b8d149c30b8307723cbe6b6e8847cb30c
