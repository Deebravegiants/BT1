# [M] decompress: Arbitrary File Write via Archive Extraction (Zip Slip)

## Summary
Severity: Medium
Advisory: GHSA-h39j-r5qq-r9mm
CVE: CVE-2026-10732
CWE: CWE-22, CWE-29
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-h39j-r5qq-r9mm
Type: github-advisory

## Affected
- npm: `decompress` — affected >=0

## Details
All versions of the package decompress are vulnerable to Arbitrary File Write via Archive Extraction (Zip Slip) when extracting a ZIP archive containing two entries with the same path - the first being a symlink to an arbitrary target and the second being a regular file - the file content is written through the symlink to the target location outside the output directory. This is due to the microtask processing order that checks readlink for the second file before resolving symlink for the first file. An attacker can write arbitrary files on the host filesystem potentially leading to remote code execution by providing a specially crafted ZIP archive.

**Note:**

This bypasses all existing path traversal protections including preventWritingThroughSymlink, added as a part of the fix for [CVE-2020-12265](https://security.snyk.io/vuln/SNYK-JS-DECOMPRESS-557358).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10732
- https://github.com/kevva/decompress/pull/112
- https://access.redhat.com/security/cve/CVE-2026-10732
- https://bugzilla.redhat.com/show_bug.cgi?id=2485376
- https://gist.github.com/Alemmi/409c3cc148c39522c6d6a8538b0e1f9e
- https://github.com/kevva/decompress
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-10732.json
- https://security.snyk.io/vuln/SNYK-JS-DECOMPRESS-16415209
