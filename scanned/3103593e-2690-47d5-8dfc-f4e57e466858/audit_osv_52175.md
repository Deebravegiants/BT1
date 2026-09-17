# [M] CVE-2021-47163

## Summary
Severity: Medium
Advisory: CVE-2021-47163
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47163
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: wait and exit until all work queues are done

On some host, a crash could be triggered simply by repeating these
commands several times:

  # modprobe tipc
  # tipc bearer enable media udp name UDP1 localip 127.0.0.1
  # rmmod tipc

  [] BUG: unable to handle kernel paging request at ffffffffc096bb00
  [] Workqueue: events 0xffffffffc096bb00
  [] Call Trace:
  []  ? process_one_work+0x1a7/0x360
  []  ? worker_thread+0x30/0x390
  []  ? create_worker+0x1a0/0x1a0
  []  ? kthread+0x116/0x130
  []  ? kthread_flush_work_fn+0x10/0x10
  []  ? ret_from_fork+0x35/0x40

When removing the TIPC module, the UDP tunnel sock will be delayed to
release in a work queue as sock_release() can't be done in rtnl_lock().
If the work queue is schedule to run after the TIPC module is removed,
kernel will crash as the work queue function cleanup_beareri() code no
longer exists when trying to invoke it.

To fix it, this patch introduce a member wq_count in tipc_net to track
the numbers of work queues in schedule, and  wait and exit until all
work queues are done in tipc_exit_net().

## References
- https://git.kernel.org/stable/c/04c26faa51d1e2fe71cf13c45791f5174c37f986
- https://git.kernel.org/stable/c/5195ec5e365a2a9331bfeb585b613a6e94f98dba
- https://git.kernel.org/stable/c/b9f5b7ad4ac3af006443f535b1ce7bff1d130d7d
- https://git.kernel.org/stable/c/d1f76dfadaf8f47ed1753f97dbcbd41c16215ffa
