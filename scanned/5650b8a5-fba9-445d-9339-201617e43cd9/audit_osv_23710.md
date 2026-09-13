# [M] driver core: fix deadlock in __device_attach

## Summary
Severity: Medium
Advisory: CVE-2022-49371
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49371
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver core: fix deadlock in __device_attach

In __device_attach function, The lock holding logic is as follows:
...
__device_attach
device_lock(dev)      // get lock dev
  async_schedule_dev(__device_attach_async_helper, dev); // func
    async_schedule_node
      async_schedule_node_domain(func)
        entry = kzalloc(sizeof(struct async_entry), GFP_ATOMIC);
	/* when fail or work limit, sync to execute func, but
	   __device_attach_async_helper will get lock dev as
	   well, which will lead to A-A deadlock.  */
	if (!entry || atomic_read(&entry_count) > MAX_WORK) {
	  func;
	else
	  queue_work_node(node, system_unbound_wq, &entry->work)
  device_unlock(dev)

As shown above, when it is allowed to do async probes, because of
out of memory or work limit, async work is not allowed, to do
sync execute instead. it will lead to A-A deadlock because of
__device_attach_async_helper getting lock dev.

To fix the deadlock, move the async_schedule_dev outside device_lock,
as we can see, in async_schedule_node_domain, the parameter of
queue_work_node is system_unbound_wq, so it can accept concurrent
operations. which will also not change the code logic, and will
not lead to deadlock.

## References
- https://git.kernel.org/stable/c/34fdd9b7def9d2fcb71bb7b0bc4848dd7313767e
- https://git.kernel.org/stable/c/36ee9ffca8ef56c302f2855c4a5fccf61c0c1ada
- https://git.kernel.org/stable/c/593b595332bd2d65e1a5c1ae7897996c157f5468
- https://git.kernel.org/stable/c/b232b02bf3c205b13a26dcec08e53baddd8e59ed
- https://git.kernel.org/stable/c/d53a227bfcd5160ce1b61d9954901968a20651e7
- https://git.kernel.org/stable/c/df6de52b80aa3b46f5ac804412355ffe2e1df93e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49371.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49371
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
