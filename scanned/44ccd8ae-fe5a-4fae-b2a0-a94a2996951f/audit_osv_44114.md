# [C] rclone before 1.74.4 Security Token Disclosure via HTTPS to HTTP Redirect

## Summary
Severity: Critical
Advisory: CVE-2026-79782
Aliases: GHSA-gx4c-2hqx-cw2r, GO-2026-6196
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79782
Type: osv

## Details
rclone before 1.74.4 fails to strip the X-Amz-Security-Token header when an S3 redirect changes scheme from HTTPS to HTTP on the same host. Attackers can intercept plaintext HTTP traffic to capture AWS STS session tokens sent in request headers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79782.json
- https://github.com/rclone/rclone/security/advisories/GHSA-gx4c-2hqx-cw2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-79782
- https://www.vulncheck.com/advisories/rclone-before-security-token-disclosure-via-https-to-http-redirect
