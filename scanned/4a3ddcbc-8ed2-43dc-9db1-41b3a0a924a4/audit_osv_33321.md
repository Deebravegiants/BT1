# [H] ksmbd: fix recursive locking in RPC handle list access

## Summary
Severity: High
Advisory: CVE-2025-40090
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-40090
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.53 <6.12.55, >=6.17.3 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix recursive locking in RPC handle list access

Since commit 305853cce3794 ("ksmbd: Fix race condition in RPC handle list
access"), ksmbd_session_rpc_method() attempts to lock sess->rpc_lock.

This causes hung connections / tasks when a client attempts to open
a named pipe. Using Samba's rpcclient tool:

 $ rpcclient //192.168.1.254 -U user%password
 $ rpcclient $> srvinfo
 <connection hung here>

Kernel side:
  "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
  task:kworker/0:0 state:D stack:0 pid:5021 tgid:5021 ppid:2 flags:0x00200000
  Workqueue: ksmbd-io handle_ksmbd_work
  Call trace:
  __schedule from schedule+0x3c/0x58
  schedule from schedule_preempt_disabled+0xc/0x10
  schedule_preempt_disabled from rwsem_down_read_slowpath+0x1b0/0x1d8
  rwsem_down_read_slowpath from down_read+0x28/0x30
  down_read from ksmbd_session_rpc_method+0x18/0x3c
  ksmbd_session_rpc_method from ksmbd_rpc_open+0x34/0x68
  ksmbd_rpc_open from ksmbd_session_rpc_open+0x194/0x228
  ksmbd_session_rpc_open from create_smb2_pipe+0x8c/0x2c8
  create_smb2_pipe from smb2_open+0x10c/0x27ac
  smb2_open from handle_ksmbd_work+0x238/0x3dc
  handle_ksmbd_work from process_scheduled_works+0x160/0x25c
  process_scheduled_works from worker_thread+0x16c/0x1e8
  worker_thread from kthread+0xa8/0xb8
  kthread from ret_from_fork+0x14/0x38
  Exception stack(0x8529ffb0 to 0x8529fff8)

The task deadlocks because the lock is already held:
  ksmbd_session_rpc_open
    down_write(&sess->rpc_lock)
    ksmbd_rpc_open
      ksmbd_session_rpc_method
        down_read(&sess->rpc_lock)   <-- deadlock

Adjust ksmbd_session_rpc_method() callers to take the lock when necessary.

## References
- https://git.kernel.org/stable/c/1891abe832cbf5a11039e088766131d0f1642d02
- https://git.kernel.org/stable/c/3412fbd81b46b9cfae013817b61d4bbd27e09e36
- https://git.kernel.org/stable/c/4602b8cee1481dbb896182e5cb1e8cf12910e9e7
- https://git.kernel.org/stable/c/5493571f4351f74e11db9943e98a07c56467cf7e
- https://git.kernel.org/stable/c/88f170814fea74911ceab798a43cbd7c5599bed4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40090.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
