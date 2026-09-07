# [M] Velocidex Velociraptor has an Incorrect Authorization issue

## Summary
Severity: Medium
Advisory: GHSA-2v93-vp82-cjv8
CVE: CVE-2026-6863
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-2v93-vp82-cjv8
Type: github-advisory

## Affected
- Go: `www.velocidex.com/golang/velociraptor` — affected >=0 <0.76.4

## Details
Velociraptor versions prior to 0.76.4 contain a cross organization authorization bypass in the HTTP API. A user with only the reader role in the root organization (the lowest authenticated role, holding only READ_RESULTS permission ) can issue a single authenticated HTTP GET that can read any files from other orgs - even if they have no explicit permissions in the target org.



However, the problem does not occur in reverse - a user with read access to a sub org is unable to read from other org or the root org.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6863
- https://docs.velociraptor.app/announcements/advisories/cve-2026-6863
- https://github.com/Velocidex/velociraptor
