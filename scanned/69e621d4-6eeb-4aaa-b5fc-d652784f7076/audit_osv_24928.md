# [M] CVE-2023-28488

## Summary
Severity: Medium
Advisory: CVE-2023-28488
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-28488
Type: osv

## Details
client.c in gdhcp in ConnMan through 1.41 could be used by network-adjacent attackers (operating a crafted DHCP server) to cause a stack-based buffer overflow and denial of service, terminating the connman process.

## References
- https://github.com/moehw/poc_exploits/tree/master/CVE-2023-28488
- https://kernel.googlesource.com/pub/scm/network/connman/connman/+/99e2c16ea1cced34a5dc450d76287a1c3e762138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28488.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28488
- https://www.debian.org/security/2023/dsa-5416
- https://lists.debian.org/debian-lts-announce/2023/04/msg00024.html
