# [C] libceph: prevent potential out-of-bounds reads in handle_auth_done()

## Summary
Severity: Critical
Advisory: CVE-2026-22984
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-22984
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.198, >=5.16.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: prevent potential out-of-bounds reads in handle_auth_done()

Perform an explicit bounds check on payload_len to avoid a possible
out-of-bounds access in the callout.

[ idryomov: changelog ]

## References
- https://git.kernel.org/stable/c/194cfe2af4d2a1de599d39dad636b47c2f6c2c96
- https://git.kernel.org/stable/c/2802ef3380fa8c4a08cda51ec1f085b1a712e9e2
- https://git.kernel.org/stable/c/2d653bb63d598ae4b096dd678744bdcc34ee89e8
- https://git.kernel.org/stable/c/79fe3511db416d2f2edcfd93569807cb02736e5e
- https://git.kernel.org/stable/c/818156caffbf55cb4d368f9c3cac64e458fb49c9
- https://git.kernel.org/stable/c/ef208ea331ef688729f64089b895ed1b49e842e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22984.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22984
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
