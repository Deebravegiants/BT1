# [H] io_uring/io-wq: Use set_bit() and test_bit() at worker->flags

## Summary
Severity: High
Advisory: CVE-2024-39508
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39508
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/io-wq: Use set_bit() and test_bit() at worker->flags

Utilize set_bit() and test_bit() on worker->flags within io_uring/io-wq
to address potential data races.

The structure io_worker->flags may be accessed through various data
paths, leading to concurrency issues. When KCSAN is enabled, it reveals
data races occurring in io_worker_handle_work and
io_wq_activate_free_worker functions.

	 BUG: KCSAN: data-race in io_worker_handle_work / io_wq_activate_free_worker
	 write to 0xffff8885c4246404 of 4 bytes by task 49071 on cpu 28:
	 io_worker_handle_work (io_uring/io-wq.c:434 io_uring/io-wq.c:569)
	 io_wq_worker (io_uring/io-wq.c:?)
<snip>

	 read to 0xffff8885c4246404 of 4 bytes by task 49024 on cpu 5:
	 io_wq_activate_free_worker (io_uring/io-wq.c:? io_uring/io-wq.c:285)
	 io_wq_enqueue (io_uring/io-wq.c:947)
	 io_queue_iowq (io_uring/io_uring.c:524)
	 io_req_task_submit (io_uring/io_uring.c:1511)
	 io_handle_tw_list (io_uring/io_uring.c:1198)
<snip>

Line numbers against commit 18daea77cca6 ("Merge tag 'for-linus' of
git://git.kernel.org/pub/scm/virt/kvm/kvm").

These races involve writes and reads to the same memory location by
different tasks running on different CPUs. To mitigate this, refactor
the code to use atomic operations such as set_bit(), test_bit(), and
clear_bit() instead of basic "and" and "or" operations. This ensures
thread-safe manipulation of worker flags.

Also, move `create_index` to avoid holes in the structure.

## References
- https://git.kernel.org/stable/c/1cbb0affb15470a9621267fe0a8568007553a4bf
- https://git.kernel.org/stable/c/8a565304927fbd28c9f028c492b5c1714002cbab
- https://git.kernel.org/stable/c/ab702c3483db9046bab9f40306f1a28b22dbbdc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39508.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39508
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
