# [M] ceph: fix possible deadlock when holding Fwb to get inline_data

## Summary
Severity: Medium
Advisory: CVE-2022-49296
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49296
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix possible deadlock when holding Fwb to get inline_data

1, mount with wsync.
2, create a file with O_RDWR, and the request was sent to mds.0:

   ceph_atomic_open()-->
     ceph_mdsc_do_request(openc)
     finish_open(file, dentry, ceph_open)-->
       ceph_open()-->
         ceph_init_file()-->
           ceph_init_file_info()-->
             ceph_uninline_data()-->
             {
               ...
               if (inline_version == 1 || /* initial version, no data */
                   inline_version == CEPH_INLINE_NONE)
                     goto out_unlock;
               ...
             }

The inline_version will be 1, which is the initial version for the
new create file. And here the ci->i_inline_version will keep with 1,
it's buggy.

3, buffer write to the file immediately:

   ceph_write_iter()-->
     ceph_get_caps(file, need=Fw, want=Fb, ...);
     generic_perform_write()-->
       a_ops->write_begin()-->
         ceph_write_begin()-->
           netfs_write_begin()-->
             netfs_begin_read()-->
               netfs_rreq_submit_slice()-->
                 netfs_read_from_server()-->
                   rreq->netfs_ops->issue_read()-->
                     ceph_netfs_issue_read()-->
                     {
                       ...
                       if (ci->i_inline_version != CEPH_INLINE_NONE &&
                           ceph_netfs_issue_op_inline(subreq))
                         return;
                       ...
                     }
     ceph_put_cap_refs(ci, Fwb);

The ceph_netfs_issue_op_inline() will send a getattr(Fsr) request to
mds.1.

4, then the mds.1 will request the rd lock for CInode::filelock from
the auth mds.0, the mds.0 will do the CInode::filelock state transation
from excl --> sync, but it need to revoke the Fxwb caps back from the
clients.

While the kernel client has aleady held the Fwb caps and waiting for
the getattr(Fsr).

It's deadlock!

URL: https://tracker.ceph.com/issues/55377

## References
- https://git.kernel.org/stable/c/292b7a7275ce535a1abfa4dd0b2e586162aaae1e
- https://git.kernel.org/stable/c/825978fd6a0defc3c29d8a38b6cea76a0938d21e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49296.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
