# [M] CVE-2017-14317

## Summary
Severity: Medium
Advisory: CVE-2017-14317
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14317
Type: osv

## Details
A domain cleanup issue was discovered in the C xenstore daemon (aka cxenstored) in Xen through 4.9.x. When shutting down a VM with a stubdomain, a race in cxenstored may cause a double-free. The xenstored daemon may crash, resulting in a DoS of any parts of the system relying on it (including domain creation / destruction, ballooning, device changes, etc.).

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- http://www.securityfocus.com/bid/100826
- http://www.securitytracker.com/id/1039350
- https://www.debian.org/security/2017/dsa-4050
- http://xenbits.xen.org/xsa/advisory-233.html
