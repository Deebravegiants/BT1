# [H] afs: Fix the maximum cell name length

## Summary
Severity: High
Advisory: CVE-2025-21646
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21646
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix the maximum cell name length

The kafs filesystem limits the maximum length of a cell to 256 bytes, but a
problem occurs if someone actually does that: kafs tries to create a
directory under /proc/net/afs/ with the name of the cell, but that fails
with a warning:

        WARNING: CPU: 0 PID: 9 at fs/proc/generic.c:405

because procfs limits the maximum filename length to 255.

However, the DNS limits the maximum lookup length and, by extension, the
maximum cell name, to 255 less two (length count and trailing NUL).

Fix this by limiting the maximum acceptable cellname length to 253.  This
also allows us to be sure we can create the "/afs/.<cell>/" mountpoint too.

Further, split the YFS VL record cell name maximum to be the 256 allowed by
the protocol and ignore the record retrieved by YFSVL.GetCellName if it
exceeds 253.

## References
- https://git.kernel.org/stable/c/7673030efe0f8ca1056d3849d61784c6caa052af
- https://git.kernel.org/stable/c/7922b1f058fe24a93730511dd0ae2e1630920096
- https://git.kernel.org/stable/c/7cb3e77e9b4e6ffa325a5559393d3283c9af3d01
- https://git.kernel.org/stable/c/8fd56ad6e7c90ac2bddb0741c6b248c8c5d56ac8
- https://git.kernel.org/stable/c/9340385468d056bb700b8f28df236b81fc86a079
- https://git.kernel.org/stable/c/aabe47cf5ac5e1db2ae0635f189d836f67024904
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21646.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
