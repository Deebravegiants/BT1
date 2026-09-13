# [H] ceph: don't leak snap_rwsem in handle_cap_grant

## Summary
Severity: High
Advisory: CVE-2022-50059
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50059
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.138, >=5.11.0 <5.15.63, >=5.16.0 <5.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: don't leak snap_rwsem in handle_cap_grant

When handle_cap_grant is called on an IMPORT op, then the snap_rwsem is
held and the function is expected to release it before returning. It
currently fails to do that in all cases which could lead to a deadlock.

## References
- https://git.kernel.org/stable/c/58dd4385577ed7969b80cdc9e2a31575aba6c712
- https://git.kernel.org/stable/c/a090cc69699ec2d11b5e34cee8c61f0d4b0068cb
- https://git.kernel.org/stable/c/aee18421bda6bf12a7cba6a3d7751c0e1cfd0094
- https://git.kernel.org/stable/c/f546faa216d0f53a42ca73ba1fd8c48765b22d77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50059.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50059
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
