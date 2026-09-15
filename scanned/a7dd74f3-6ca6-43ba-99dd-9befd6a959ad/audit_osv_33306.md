# [H] vhost: vringh: Modify the return value check

## Summary
Severity: High
Advisory: CVE-2025-40051
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40051
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost: vringh: Modify the return value check

The return value of copy_from_iter and copy_to_iter can't be negative,
check whether the copied lengths are equal.

## References
- https://git.kernel.org/stable/c/78dc7362662fedaa1928fb8e4f27401c8322905d
- https://git.kernel.org/stable/c/82a8d0fda55b35361ee7f35b54fa2b66d7847d2b
- https://git.kernel.org/stable/c/baa37b1c7e29546f79c39bef0d18c4edc9f39bb1
- https://git.kernel.org/stable/c/cfa0654402c06d086201a9ff167eb95da5844fc3
- https://git.kernel.org/stable/c/db042925a5ab7a550b710addeadbf6f72e3a8a4b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40051.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40051
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
