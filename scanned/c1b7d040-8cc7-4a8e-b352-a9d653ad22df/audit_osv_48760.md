# [M] CVE-2018-12563

## Summary
Severity: Medium
Advisory: CVE-2018-12563
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12563
Type: osv

## Details
An issue was discovered in Linaro LAVA before 2018.5.post1. Because of support for file: URLs, a user can force lava-server-gunicorn to download any file from the filesystem if it's readable by lavaserver and valid yaml.

## References
- https://git.linaro.org/lava/lava.git/commit/?id=e24ec39599bc07562ad8bc2a581144b8448cb214
