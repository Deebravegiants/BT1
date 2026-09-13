# [H] netfilter: ipset: add missing range check in bitmap_ip_uadt

## Summary
Severity: High
Advisory: CVE-2024-53141
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-06
Source: https://osv.dev/vulnerability/CVE-2024-53141
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: add missing range check in bitmap_ip_uadt

When tb[IPSET_ATTR_IP_TO] is not present but tb[IPSET_ATTR_CIDR] exists,
the values of ip and ip_to are slightly swapped. Therefore, the range check
for ip should be done later, but this part is missing and it seems that the
vulnerability occurs.

So we should add missing range checks and remove unnecessary range checks.

## References
- https://git.kernel.org/stable/c/15794835378ed56fb9bacc6a5dd3b9f33520604e
- https://git.kernel.org/stable/c/2e151b8ca31607d14fddc4ad0f14da0893e1a7c7
- https://git.kernel.org/stable/c/35f56c554eb1b56b77b3cf197a6b00922d49033d
- https://git.kernel.org/stable/c/3c20b5948f119ae61ee35ad8584d666020c91581
- https://git.kernel.org/stable/c/591efa494a1cf649f50a35def649c43ae984cd03
- https://git.kernel.org/stable/c/78b0f2028f1043227a8eb0c41944027fc6a04596
- https://git.kernel.org/stable/c/7ffef5e5d5eeecd9687204a5ec2d863752aafb7e
- https://git.kernel.org/stable/c/856023ef032d824309abd5c747241dffa33aae8c
- https://git.kernel.org/stable/c/e67471437ae9083fa73fa67eee1573fec1b7c8cf
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53141.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
