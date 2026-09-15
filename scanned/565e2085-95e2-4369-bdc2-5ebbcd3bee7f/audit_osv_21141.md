# [M] CVE-2021-40886

## Summary
Severity: Medium
Advisory: CVE-2021-40886
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-40886
Type: osv

## Details
Projectsend version r1295 is affected by a directory traversal vulnerability. A user with Uploader role can add value `2` for `chunks` parameter to bypass `fileName` sanitization.

## References
- https://github.com/projectsend/projectsend/issues/993
