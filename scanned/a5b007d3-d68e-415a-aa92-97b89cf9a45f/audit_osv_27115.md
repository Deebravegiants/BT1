# [M] Cookie without Secure attribute in phpipam/phpipam

## Summary
Severity: Medium
Advisory: CVE-2024-10718
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10718
Type: osv

## Details
In phpipam/phpipam version 1.5.1, the Secure attribute for sensitive cookies in HTTPS sessions is not set. This could cause the user agent to send those cookies in plaintext over an HTTP session, potentially exposing sensitive information. The issue is fixed in version 1.7.0.

## References
- https://huntr.com/bounties/725bce8f-328f-4fbc-acf5-46ea920cd3c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10718.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10718
- https://github.com/phpipam/phpipam/commit/ddf70ef6801442eb8b0be5eea829e470e653c70e
