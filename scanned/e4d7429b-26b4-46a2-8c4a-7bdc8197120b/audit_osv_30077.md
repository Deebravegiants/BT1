# [H] r8169: add tally counter fields added with RTL8125

## Summary
Severity: High
Advisory: CVE-2024-49973
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49973
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

r8169: add tally counter fields added with RTL8125

RTL8125 added fields to the tally counter, what may result in the chip
dma'ing these new fields to unallocated memory. Therefore make sure
that the allocated memory area is big enough to hold all of the
tally counter values, even if we use only parts of it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/1c723d785adb711496bc64c24240f952f4faaabf
- https://git.kernel.org/stable/c/21950321ad33d7613b1453f4c503d7b1871deb61
- https://git.kernel.org/stable/c/585c048d15ed559f20cb94c8fa2f30077efa4fbc
- https://git.kernel.org/stable/c/64648ae8c97ec5a3165021627f5a1658ebe081ca
- https://git.kernel.org/stable/c/92bc8647b4d65f4d4bf8afdb206321c1bc55a486
- https://git.kernel.org/stable/c/991e8b0bab669b7d06927c3e442b3352532e8581
- https://git.kernel.org/stable/c/ced8e8b8f40accfcce4a2bbd8b150aa76d5eff9a
- https://git.kernel.org/stable/c/fe44b3bfbf0c74df5712f44458689d0eccccf47d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49973.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
