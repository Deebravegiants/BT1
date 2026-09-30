# [H] Chamilo LMS has Arbitrary File Upload via MIME-Only Validation in Exercise Sound Upload Leads to RCE

## Summary
Severity: High
Advisory: CVE-2026-32931
Aliases: GHSA-863j-h6pf-3xhx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-32931
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, an unrestricted file upload vulnerability in the exercise sound upload function allows an authenticated teacher to upload a PHP webshell by spoofing the Content-Type header to audio/mpeg. The uploaded file retains its original .php extension and is placed in a web-accessible directory, enabling Remote Code Execution as the web server user (www-data). This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32931.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-863j-h6pf-3xhx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32931
- https://github.com/chamilo/chamilo-lms/commit/8cbe660de267f2b6ed625433bdfcf38dee8752b4
- https://github.com/chamilo/chamilo-lms/commit/d5ef5153df3d1b2de112cbeb190cdd10bea457f3
