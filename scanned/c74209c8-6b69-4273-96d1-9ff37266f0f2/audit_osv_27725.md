# [C] CVE-2024-25191

## Summary
Severity: Critical
Advisory: CVE-2024-25191
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2024-25191
Type: osv

## Details
php-jwt 1.0.0 uses strcmp (which is not constant time) to verify authentication, which makes it easier to bypass authentication via a timing side channel.

## References
- https://github.com/P3ngu1nW/CVE_Request/blob/main/cdoco%3Aphp-jwt.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25191.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25191
