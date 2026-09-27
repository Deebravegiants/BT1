# [C] Velociraptor vulnerability in the query() plugin which allows access to all orgs with the user's current ACL token

## Summary
Severity: Critical
Advisory: GHSA-hv5g-26jg-pc45
CVE: CVE-2026-6290
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-hv5g-26jg-pc45
Type: github-advisory

## Affected
- Go: `www.velocidex.com/golang/velociraptor` — affected >=0

## Details
Velociraptor versions prior to 0.76.3 contain a vulnerability in the query() plugin which allows access to all orgs with the user's current ACL token. This allows an authenticated GUI user with access in one org, to use the query() plugin, in a notebook cell, to run VQL queries on other orgs which they may not have access to. The user's permissions in the other org are
the same as the permissions they have in the org containing the notebook.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6290
- https://docs.velociraptor.app/announcements/advisories/cve-2026-6290
- https://github.com/Velocidex/velociraptor
