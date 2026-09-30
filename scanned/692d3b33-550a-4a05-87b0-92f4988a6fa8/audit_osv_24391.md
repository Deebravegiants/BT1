# [H] CVE-2023-1390

## Summary
Severity: High
Advisory: CVE-2023-1390
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-16
Source: https://osv.dev/vulnerability/CVE-2023-1390
Type: osv

## Details
A remote denial of service vulnerability was found in the Linux kernel’s TIPC kernel module. The while loop in tipc_link_xmit() hits an unknown state while attempting to parse SKBs, which are not in the queue. Sending two small UDP packets to a system with a UDP bearer results in the CPU utilization for the system to instantly spike to 100%, causing a denial of service condition.

## References
- https://gist.github.com/netspooky/bee2d07022f6350bb88eaa48e571d9b5
- https://infosec.exchange/%40_mattata/109427999461122360
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1390.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1390
- https://security.netapp.com/advisory/ntap-20230420-0001/
- https://github.com/torvalds/linux/commit/b77413446408fdd256599daf00d5be72b5f3e7c6
