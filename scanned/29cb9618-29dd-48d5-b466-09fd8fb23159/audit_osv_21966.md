# [H] Out-of-bound write in tcp_flags

## Summary
Severity: High
Advisory: CVE-2022-1841
Aliases: GHSA-5c3j-p8cr-2pgh
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-1841
Type: osv

## Details
In subsys/net/ip/tcp.c , function tcp_flags , when the incoming parameter flags is ECN or CWR , the buf will out-of-bounds write a byte zero.

## References
- http://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-5c3j-p8cr-2pgh
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1841.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1841
