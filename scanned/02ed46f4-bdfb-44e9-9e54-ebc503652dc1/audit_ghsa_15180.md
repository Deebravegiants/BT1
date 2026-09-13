# [H] Gentoo Portage missing PGP validation of executed code

## Summary
Severity: High
Advisory: GHSA-pw5x-x5jw-ccmh
CVE: CVE-2016-20021
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-12
Source: https://github.com/advisories/GHSA-pw5x-x5jw-ccmh
Type: github-advisory

## Affected
- PyPI: `portage` — affected >=0 <3.0.47

## Details
In Gentoo Portage before 3.0.47, there is missing PGP validation of executed code: the standalone emerge-webrsync downloads a .gpgsig file but does not perform signature verification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-20021
- https://github.com/gentoo/portage/commit/28cd240fb23d880b8641a058831c6762db71c3e2
- https://bugs.gentoo.org/597800
- https://github.com/gentoo/portage
- https://github.com/pypa/advisory-database/tree/main/vulns/portage/PYSEC-2024-10.yaml
- https://gitweb.gentoo.org/proj/portage.git/tree/NEWS
- https://gitweb.gentoo.org/repo/gentoo.git/commit/?id=5b3c80502e96406b4b175e2ee79eb65f3f3cd9f6
- https://wiki.gentoo.org/wiki/Portage
