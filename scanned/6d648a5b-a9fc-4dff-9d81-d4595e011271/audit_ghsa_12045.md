# [H] Black: Arbitrary file writes from unsanitized user input in cache file name

## Summary
Severity: High
Advisory: GHSA-3936-cmfr-pm3m
CVE: CVE-2026-32274
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-3936-cmfr-pm3m
Type: github-advisory

## Affected
- PyPI: `black` — affected >=24.3.0 <26.3.1

## Details
### Impact

Black writes a cache file, the name of which is computed from various formatting options. The value of the `--python-cell-magics` option was placed in the filename without sanitization, which allowed an attacker who controls the value of this argument to write cache files to arbitrary file system locations. 

### Patches

Fixed in Black 26.3.1.

### Workarounds

Do not allow untrusted user input into the value of the `--python-cell-magics` option.

## References
- https://github.com/psf/black/security/advisories/GHSA-3936-cmfr-pm3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32274
- https://github.com/psf/black/pull/4176
- https://github.com/psf/black/pull/5038
- https://github.com/psf/black/commit/4937fe6cf241139ddbfc16b0bdbb5b422798909d
- https://github.com/psf/black/commit/ed770ba4dd50c419148a0fca2b43937a7447e1f9
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/errata/RHSA-2026:13545
- https://access.redhat.com/errata/RHSA-2026:13553
- https://access.redhat.com/security/cve/CVE-2026-32274
- https://bugzilla.redhat.com/show_bug.cgi?id=2447111
- https://github.com/psf/black
- https://github.com/psf/black/releases/tag/26.3.1
- https://github.com/pypa/advisory-database/tree/main/vulns/black/PYSEC-2026-2121.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32274.json
