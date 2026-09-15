# [H] fhandle: fix UAF due to unlocked ->mnt_ns read in may_decode_fh()

## Summary
Severity: High
Advisory: CVE-2026-53341
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-53341
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.95, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

fhandle: fix UAF due to unlocked ->mnt_ns read in may_decode_fh()

may_decode_fh() accesses mount::mnt_ns without holding any locks; that
means the mount can concurrently be unmounted, and the mnt_namespace can
concurrently be freed after an RCU grace period.

This race can happens as follows, assuming that the mount point was
created by open_tree(..., OPEN_TREE_CLONE):

thread 1            thread 2            RCU
                    __do_sys_open_by_handle_at
                      do_handle_open
                        handle_to_path
                          may_decode_fh
                            is_mounted
                              [mount::mnt_ns access]
                            [mount::mnt_ns access]
__do_sys_close
  fput_close_sync
    __fput
      dissolve_on_fput
        umount_tree
        class_namespace_excl_destructor
          namespace_unlock
            free_mnt_ns
              mnt_ns_tree_remove
                call_rcu(mnt_ns_release_rcu)
                                        mnt_ns_release_rcu
                                          mnt_ns_release
                                            kfree
                            [mnt_namespace::user_ns access] **UAF**

Fix it by taking rcu_read_lock() around the mount::mnt_ns access, like
in __prepend_path().
Additionally, document the semantics of mount::mnt_ns, and use WRITE_ONCE()
for writers that can race with lockless readers.

This bug is unreachable unless one of the following is set:

 - CONFIG_PREEMPTION
 - CONFIG_RCU_STRICT_GRACE_PERIOD

because it requires an RCU grace period to happen during a syscall without
an explicit preemption.

This doesn't seem to have interesting security impact; worst-case, it could
leak the result of an integer comparison to userspace (from the level
check in cap_capable()), cause an endless loop, or crash the kernel by
dereferencing an invalid address.

## References
- https://git.kernel.org/stable/c/15ea8dc42a02259d49dee38a658d40f60fcd75ed
- https://git.kernel.org/stable/c/32138633e51e6db59e474765cf93268c92b42888
- https://git.kernel.org/stable/c/40ab6644b99685755f740b872c00ef40d9aa870e
- https://git.kernel.org/stable/c/a8ed2c29fcfdac78db96c9da4e659c8a513f2a94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53341.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
