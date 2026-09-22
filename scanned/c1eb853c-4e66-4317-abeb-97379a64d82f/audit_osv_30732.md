# [M] pwndoc's UnhandledPromiseRejection on audits causes Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: CVE-2024-55653
Aliases: GHSA-ggqg-3f7v-c8rc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-10
Source: https://osv.dev/vulnerability/CVE-2024-55653
Type: osv

## Details
PwnDoc is a penetration test report generator. In versions up to and including 0.5.3, an authenticated user is able to crash the backend by raising a `UnhandledPromiseRejection` on audits which exits the backend. The user doesn't need to know the audit id, since a bad audit id will also raise the rejection. With the backend being unresponsive, the whole application becomes unusable for all users of the application. As of time of publication, no known patches are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55653.json
- https://github.com/pwndoc/pwndoc/security/advisories/GHSA-ggqg-3f7v-c8rc
- https://nvd.nist.gov/vuln/detail/CVE-2024-55653
