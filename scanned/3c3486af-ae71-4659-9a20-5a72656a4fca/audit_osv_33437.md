# [H] ceph: fix multifs mds auth caps issue

## Summary
Severity: High
Advisory: CVE-2025-40362
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-40362
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix multifs mds auth caps issue

The mds auth caps check should also validate the
fsname along with the associated caps. Not doing
so would result in applying the mds auth caps of
one fs on to the other fs in a multifs ceph cluster.
The bug causes multiple issues w.r.t user
authentication, following is one such example.

Steps to Reproduce (on vstart cluster):
1. Create two file systems in a cluster, say 'fsname1' and 'fsname2'
2. Authorize read only permission to the user 'client.usr' on fs 'fsname1'
    $ceph fs authorize fsname1 client.usr / r
3. Authorize read and write permission to the same user 'client.usr' on fs 'fsname2'
    $ceph fs authorize fsname2 client.usr / rw
4. Update the keyring
    $ceph auth get client.usr >> ./keyring

With above permssions for the user 'client.usr', following is the
expectation.
  a. The 'client.usr' should be able to only read the contents
     and not allowed to create or delete files on file system 'fsname1'.
  b. The 'client.usr' should be able to read/write on file system 'fsname2'.

But, with this bug, the 'client.usr' is allowed to read/write on file
system 'fsname1'. See below.

5. Mount the file system 'fsname1' with the user 'client.usr'
     $sudo bin/mount.ceph usr@.fsname1=/ /kmnt_fsname1_usr/
6. Try creating a file on file system 'fsname1' with user 'client.usr'. This
   should fail but passes with this bug.
     $touch /kmnt_fsname1_usr/file1
7. Mount the file system 'fsname1' with the user 'client.admin' and create a
   file.
     $sudo bin/mount.ceph admin@.fsname1=/ /kmnt_fsname1_admin
     $echo "data" > /kmnt_fsname1_admin/admin_file1
8. Try removing an existing file on file system 'fsname1' with the user
   'client.usr'. This shoudn't succeed but succeeds with the bug.
     $rm -f /kmnt_fsname1_usr/admin_file1

For more information, please take a look at the corresponding mds/fuse patch
and tests added by looking into the tracker mentioned below.

v2: Fix a possible null dereference in doutc
v3: Don't store fsname from mdsmap, validate against
    ceph_mount_options's fsname and use it
v4: Code refactor, better warning message and
    fix possible compiler warning

[ Slava.Dubeyko: "fsname check failed" -> "fsname mismatch" ]

## References
- https://git.kernel.org/stable/c/07640d34a781bb2e39020a39137073c03c4aa932
- https://git.kernel.org/stable/c/22c73d52a6d05c5a2053385c0d6cd9984732799d
- https://git.kernel.org/stable/c/ca3da8b27ab9a0923ad477447cfb8fc7f4b4c523
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40362.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40362
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
