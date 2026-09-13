# [M] CVE-2018-12564

## Summary
Severity: Medium
Advisory: CVE-2018-12564
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12564
Type: osv

## Details
An issue was discovered in Linaro LAVA before 2018.5.post1. Because of support for URLs in the submit page, a user can forge an HTTP request that will force lava-server-gunicorn to return any file on the server that is readable by lavaserver and valid yaml.

## References
- https://lists.debian.org/debian-lts-announce/2018/06/msg00011.html
- https://www.debian.org/security/2018/dsa-4234
- https://git.linaro.org/lava/lava.git/commit/?id=95a9a77b144ced24d7425d6544ab03ca7f6c75d3
