# [C] CVE-2024-25181

## Summary
Severity: Critical
Advisory: CVE-2024-25181
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2024-25181
Type: osv

## Details
A critical vulnerability has been identified in givanz VvvebJs 1.7.2, which allows both Server-Side Request Forgery (SSRF) and arbitrary file reading. The vulnerability stems from improper handling of user-supplied URLs in the "file_get_contents" function within the "save.php" file.

## References
- https://gist.github.com/joaoviictorti/69cbae23d98fb9a1a4b3eee0c305c7de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25181.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25181
