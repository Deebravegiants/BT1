# [H] Filestash allows attackers to escalate privileges via sending a crafted request

## Summary
Severity: High
Advisory: GHSA-rcqf-cpv9-g5jf
CVE: CVE-2026-50891
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-rcqf-cpv9-g5jf
Type: github-advisory

## Affected
- Go: `github.com/mickael-kerjean/filestash` — affected >=0

## Details
Incorrect access control in the /admin/api/config component of Filestash v0.4.0 allows attackers to escalate privileges via sending a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50891
- https://gist.github.com/pyuysig/50dc365f54f95396bb67532f02b34bb0
- https://github.com/mickael-kerjean/filestash
