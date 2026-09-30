# [M] Code injection in dye template expressions

## Summary
Severity: Medium
Advisory: CVE-2026-35197
Aliases: GHSA-3v4r-5vfh-3wjr
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35197
Type: osv

## Details
dye is a portable and respectful color library for shell scripts. Prior to 1.1.1, certain dye template expressions would result in execution of arbitrary code. This issue was discovered and fixed by dye's author, and is not known to be exploited. This vulnerability is fixed in 1.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35197.json
- https://github.com/mattieb/dye/security/advisories/GHSA-3v4r-5vfh-3wjr
- https://mattiebee.io/dye-template-advisory
- https://nvd.nist.gov/vuln/detail/CVE-2026-35197
