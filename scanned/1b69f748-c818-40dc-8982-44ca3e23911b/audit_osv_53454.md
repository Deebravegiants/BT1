# [H] CVE-2022-42902

## Summary
Severity: High
Advisory: CVE-2022-42902
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-13
Source: https://osv.dev/vulnerability/CVE-2022-42902
Type: osv

## Details
In Linaro Automated Validation Architecture (LAVA) before 2022.10, there is dynamic code execution in lava_server/lavatable.py. Due to improper input sanitization, an anonymous user can force the lava-server-gunicorn service to execute user-provided code on the server.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00019.html
- https://www.debian.org/security/2022/dsa-5260
- https://git.lavasoftware.org/lava/lava/-/merge_requests/1834
- https://git.lavasoftware.org/lava/lava/-/commit/e66b74cd6c175ff8826b8f3431740963be228b52?merge_request_iid=1834
