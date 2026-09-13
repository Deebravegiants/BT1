# [M] SSRF in repository migration

## Summary
Severity: Medium
Advisory: GHSA-7v5r-r995-q2x2
CVE: CVE-2022-0870
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-7v5r-r995-q2x2
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.5

## Details
Gogs is a self-hosted Git service. The malicious user is able to discover services in the internal network through repository migration functionality. All installations accepting public traffic are affected. Internal network CIDRs are prohibited to be used as repository migration targets. Users should upgrade to 0.12.5 or the latest 0.13.0+dev. Gogs should be ran in its own private network until users can update.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0870
- https://github.com/gogs/gogs/commit/91f2cde5e95f146bfe4765e837e7282df6c7cabb
- https://github.com/gogs/gogs
- https://huntr.dev/bounties/327797d7-ae41-498f-9bff-cc0bf98cf531
