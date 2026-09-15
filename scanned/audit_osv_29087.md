# [H] drm/drm_file: Fix pid refcounting race

## Summary
Severity: High
Advisory: CVE-2024-39486
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-06
Source: https://osv.dev/vulnerability/CVE-2024-39486
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.37, >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/drm_file: Fix pid refcounting race

<maarten.lankhorst@linux.intel.com>, Maxime Ripard
<mripard@kernel.org>, Thomas Zimmermann <tzimmermann@suse.de>

filp->pid is supposed to be a refcounted pointer; however, before this
patch, drm_file_update_pid() only increments the refcount of a struct
pid after storing a pointer to it in filp->pid and dropping the
dev->filelist_mutex, making the following race possible:

process A               process B
=========               =========
                        begin drm_file_update_pid
                        mutex_lock(&dev->filelist_mutex)
                        rcu_replace_pointer(filp->pid, <pid B>, 1)
                        mutex_unlock(&dev->filelist_mutex)
begin drm_file_update_pid
mutex_lock(&dev->filelist_mutex)
rcu_replace_pointer(filp->pid, <pid A>, 1)
mutex_unlock(&dev->filelist_mutex)
get_pid(<pid A>)
synchronize_rcu()
put_pid(<pid B>)   *** pid B reaches refcount 0 and is freed here ***
                        get_pid(<pid B>)   *** UAF ***
                        synchronize_rcu()
                        put_pid(<pid A>)

As far as I know, this race can only occur with CONFIG_PREEMPT_RCU=y
because it requires RCU to detect a quiescent state in code that is not
explicitly calling into the scheduler.

This race leads to use-after-free of a "struct pid".
It is probably somewhat hard to hit because process A has to pass
through a synchronize_rcu() operation while process B is between
mutex_unlock() and get_pid().

Fix it by ensuring that by the time a pointer to the current task's pid
is stored in the file, an extra reference to the pid has been taken.

This fix also removes the condition for synchronize_rcu(); I think
that optimization is unnecessary complexity, since in that case we
would usually have bailed out on the lockless check above.

## References
- https://git.kernel.org/stable/c/0acce2a5c619ef1abdee783d7fea5eac78ce4844
- https://git.kernel.org/stable/c/16682588ead4a593cf1aebb33b36df4d1e9e4ffa
- https://git.kernel.org/stable/c/4f2a129b33a2054e62273edd5a051c34c08d96e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39486.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39486
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
