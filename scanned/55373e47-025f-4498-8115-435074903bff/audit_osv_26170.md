# [H] CVE-2023-52266

## Summary
Severity: High
Advisory: CVE-2023-52266
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-30
Source: https://osv.dev/vulnerability/CVE-2023-52266
Type: osv

## Details
ehttp 1.0.6 before 17405b9 has an epoll_socket.cpp read_func use-after-free. An attacker can make many connections over a short time to trigger this.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52266.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52266
- https://github.com/hongliuliao/ehttp/issues/38
- https://github.com/hongliuliao/ehttp/commit/17405b975948abc216f6a085d2d027ec1cfd5766
