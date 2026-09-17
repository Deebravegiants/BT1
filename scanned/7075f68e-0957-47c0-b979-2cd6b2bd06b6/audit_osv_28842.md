# [M] qibfs: fix dentry leak

## Summary
Severity: Medium
Advisory: CVE-2024-36947
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36947
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

qibfs: fix dentry leak

simple_recursive_removal() drops the pinning references to all positives
in subtree.  For the cases when its argument has been kept alive by
the pinning alone that's exactly the right thing to do, but here
the argument comes from dcache lookup, that needs to be balanced by
explicit dput().

Fucked-up-by: Al Viro <viro@zeniv.linux.org.uk>

## References
- https://git.kernel.org/stable/c/02ee394a5d899d9bd2f0759382e9481cab6166f8
- https://git.kernel.org/stable/c/24dd9b08df718f20ccf2dd1519909fefd8c233ee
- https://git.kernel.org/stable/c/aa23317d0268b309bb3f0801ddd0d61813ff5afb
- https://git.kernel.org/stable/c/bd8f78c71defbcb7a9ed331e7f287507df972b00
- https://git.kernel.org/stable/c/db71ca93259dd1078bcfea3afafde2143cfc2da7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36947.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
