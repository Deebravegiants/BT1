# [C] CVE-2023-46586

## Summary
Severity: Critical
Advisory: CVE-2023-46586
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2023-46586
Type: osv

## Details
cgi.c in weborf .0.17, 0.18, 0.19, and 0.20 (before 1.0) lacks '\0' termination of the path for CGI scripts because strncpy is misused.

## References
- https://github.com/ltworf/weborf/pull/88/commits/7057d254b734dfc9cfb58983f901aa6ec3c94fd4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46586.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-46586
- https://github.com/ltworf/weborf/commit/49824204add55aab0568d90a6b1e7c822d32120d
- https://github.com/ltworf/weborf/commit/6f83c3e9ceed8b0d93608fd5d42b53c081057991
- https://github.com/ltworf/weborf/pull/88
