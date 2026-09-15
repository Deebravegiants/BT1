# [M] NLTK before 3.10.0 Arbitrary File Read via FileSystemPathPointer

## Summary
Severity: Medium
Advisory: CVE-2026-65915
Aliases: GHSA-72r2-7mfr-5xr9, PYSEC-2026-3731
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-65915
Type: osv

## Details
NLTK versions before 3.10.0 contain a logic bug in FileSystemPathPointer.open() where the sandbox validation check compares a normalized path against itself, making the security check permanently inert. Attackers can pass file:// URLs to nltk.data.load() to read arbitrary files accessible to the process user, including credentials and configuration files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65915.json
- https://github.com/nltk/nltk/security/advisories/GHSA-72r2-7mfr-5xr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-65915
- https://www.vulncheck.com/advisories/nltk-before-arbitrary-file-read-via-filesystempathpointer
