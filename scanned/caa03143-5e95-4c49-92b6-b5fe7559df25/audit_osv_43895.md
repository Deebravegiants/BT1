# [M] ArcadeDB before 26.8.1 Arbitrary File Read via Unescaped Regex

## Summary
Severity: Medium
Advisory: CVE-2026-75840
Aliases: GHSA-wx28-2265-f788
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75840
Type: osv

## Details
ArcadeDB before 26.8.1 contains an arbitrary file read vulnerability in the GraalVM JavaScript sandbox allowlist enforcement, which uses unescaped regular expressions to validate package names. Attackers with trigger creation privileges can use Java.type() to access java.util.zip.ZipFile or java.util.jar.JarFile classes and read arbitrary files on the host system as the ArcadeDB server process.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-wx28-2265-f788
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75840.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75840
- https://www.vulncheck.com/advisories/arcadedb-before-arbitrary-file-read-via-unescaped-regex
