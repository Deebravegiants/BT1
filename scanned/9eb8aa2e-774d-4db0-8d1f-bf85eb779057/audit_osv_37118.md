# [M] HTTP signature verification can be bypassed

## Summary
Severity: Medium
Advisory: CVE-2026-28432
Aliases: GHSA-grwc-c762-gcvp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-28432
Type: osv

## Details
Misskey is an open source, federated social media platform. All Misskey servers prior to 2026.3.1 contain a vulnerability that allows bypassing HTTP signature verification. Although this is a vulnerability related to federation, it affects all servers regardless of whether federation is enabled or disabled. This vulnerability is fixed in 2026.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28432.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-grwc-c762-gcvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28432
