# [M] CVE-2018-5995

## Summary
Severity: Medium
Advisory: CVE-2018-5995
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-07
Source: https://osv.dev/vulnerability/CVE-2018-5995
Type: osv

## Details
The pcpu_embed_first_chunk function in mm/percpu.c in the Linux kernel through 4.14.14 allows local users to obtain sensitive address information by reading dmesg data from a "pages/cpu" printk call.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://seclists.org/bugtraq/2019/Aug/18
- http://www.securityfocus.com/bid/105049
- https://github.com/johnsonwangqize/cve-linux/blob/master/CVE-2018-5995.md
- https://www.debian.org/security/2019/dsa-4497
