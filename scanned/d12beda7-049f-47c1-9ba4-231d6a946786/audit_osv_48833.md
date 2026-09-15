# [M] CVE-2018-15469

## Summary
Severity: Medium
Advisory: CVE-2018-15469
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/CVE-2018-15469
Type: osv

## Details
An issue was discovered in Xen through 4.11.x. ARM never properly implemented grant table v2, either in the hypervisor or in Linux. Unfortunately, an ARM guest can still request v2 grant tables; they will simply not be properly set up, resulting in subsequent grant-related hypercalls hitting BUG() checks. An unprivileged guest can cause a BUG() check in the hypervisor, resulting in a denial-of-service (crash).

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00013.html
- https://security.gentoo.org/glsa/201810-06
- http://xenbits.xen.org/xsa/advisory-268.html
