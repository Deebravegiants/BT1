# [H] ksmbd: validate zero num_subauth before sub_auth is accessed

## Summary
Severity: High
Advisory: CVE-2025-22038
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22038
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate zero num_subauth before sub_auth is accessed

Access psid->sub_auth[psid->num_subauth - 1] without checking
if num_subauth is non-zero leads to an out-of-bounds read.
This patch adds a validation step to ensure num_subauth != 0
before sub_auth is accessed.

## References
- https://git.kernel.org/stable/c/0e36a3e080d6d8bd7a34e089345d043da4ac8283
- https://git.kernel.org/stable/c/3ac65de111c686c95316ade660f8ba7aea3cd3cc
- https://git.kernel.org/stable/c/56de7778a48560278c334077ace7b9ac4bfb2fd1
- https://git.kernel.org/stable/c/68c6c3142bfcdb049839d40a9a59ebe8ea865002
- https://git.kernel.org/stable/c/bf21e29d78cd2c2371023953d9c82dfef82ebb36
- https://git.kernel.org/stable/c/c8bfe1954a0b89e7b29b3a3e7f4c5e0ebd295e20
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22038.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22038
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
