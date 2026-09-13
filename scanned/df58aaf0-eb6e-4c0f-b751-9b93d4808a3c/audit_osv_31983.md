# [M] fs/9p: fix NULL pointer dereference on mkdir

## Summary
Severity: Medium
Advisory: CVE-2025-22070
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22070
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/9p: fix NULL pointer dereference on mkdir

When a 9p tree was mounted with option 'posixacl', parent directory had a
default ACL set for its subdirectories, e.g.:

  setfacl -m default:group:simpsons:rwx parentdir

then creating a subdirectory crashed 9p client, as v9fs_fid_add() call in
function v9fs_vfs_mkdir_dotl() sets the passed 'fid' pointer to NULL
(since dafbe689736) even though the subsequent v9fs_set_create_acl() call
expects a valid non-NULL 'fid' pointer:

  [   37.273191] BUG: kernel NULL pointer dereference, address: 0000000000000000
  ...
  [   37.322338] Call Trace:
  [   37.323043]  <TASK>
  [   37.323621] ? __die (arch/x86/kernel/dumpstack.c:421 arch/x86/kernel/dumpstack.c:434)
  [   37.324448] ? page_fault_oops (arch/x86/mm/fault.c:714)
  [   37.325532] ? search_module_extables (kernel/module/main.c:3733)
  [   37.326742] ? p9_client_walk (net/9p/client.c:1165) 9pnet
  [   37.328006] ? search_bpf_extables (kernel/bpf/core.c:804)
  [   37.329142] ? exc_page_fault (./arch/x86/include/asm/paravirt.h:686 arch/x86/mm/fault.c:1488 arch/x86/mm/fault.c:1538)
  [   37.330196] ? asm_exc_page_fault (./arch/x86/include/asm/idtentry.h:574)
  [   37.331330] ? p9_client_walk (net/9p/client.c:1165) 9pnet
  [   37.332562] ? v9fs_fid_xattr_get (fs/9p/xattr.c:30) 9p
  [   37.333824] v9fs_fid_xattr_set (fs/9p/fid.h:23 fs/9p/xattr.c:121) 9p
  [   37.335077] v9fs_set_acl (fs/9p/acl.c:276) 9p
  [   37.336112] v9fs_set_create_acl (fs/9p/acl.c:307) 9p
  [   37.337326] v9fs_vfs_mkdir_dotl (fs/9p/vfs_inode_dotl.c:411) 9p
  [   37.338590] vfs_mkdir (fs/namei.c:4313)
  [   37.339535] do_mkdirat (fs/namei.c:4336)
  [   37.340465] __x64_sys_mkdir (fs/namei.c:4354)
  [   37.341455] do_syscall_64 (arch/x86/entry/common.c:52 arch/x86/entry/common.c:83)
  [   37.342447] entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)

Fix this by simply swapping the sequence of these two calls in
v9fs_vfs_mkdir_dotl(), i.e. calling v9fs_set_create_acl() before
v9fs_fid_add().

## References
- https://git.kernel.org/stable/c/2139dea5c53e3bb63ac49a6901c85e525a80ee8a
- https://git.kernel.org/stable/c/3f61ac7c65bdb26accb52f9db66313597e759821
- https://git.kernel.org/stable/c/6517b395cb1e43fbf3962dd93e6fb4a5e5ab100e
- https://git.kernel.org/stable/c/8522051c58d68146b93e8a5ba9987e83b3d64e7b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22070.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
