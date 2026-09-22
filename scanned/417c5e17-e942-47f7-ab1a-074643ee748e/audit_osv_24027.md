# [M] ring-buffer: Check for NULL cpu_buffer in ring_buffer_wake_waiters()

## Summary
Severity: Medium
Advisory: CVE-2022-49889
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49889
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.75 <5.15.78, >=6.0.3 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Check for NULL cpu_buffer in ring_buffer_wake_waiters()

On some machines the number of listed CPUs may be bigger than the actual
CPUs that exist. The tracing subsystem allocates a per_cpu directory with
access to the per CPU ring buffer via a cpuX file. But to save space, the
ring buffer will only allocate buffers for online CPUs, even though the
CPU array will be as big as the nr_cpu_ids.

With the addition of waking waiters on the ring buffer when closing the
file, the ring_buffer_wake_waiters() now needs to make sure that the
buffer is allocated (with the irq_work allocated with it) before trying to
wake waiters, as it will cause a NULL pointer dereference.

While debugging this, I added a NULL check for the buffer itself (which is
OK to do), and also NULL pointer checks against buffer->buffers (which is
not fine, and will WARN) as well as making sure the CPU number passed in
is within the nr_cpu_ids (which is also not fine if it isn't).


Bugzilla: https://bugzilla.opensuse.org/show_bug.cgi?id=1204705

## References
- https://git.kernel.org/stable/c/49ca992f6e50d0f46ec9608f44e011cf3121f389
- https://git.kernel.org/stable/c/7433632c9ff68a991bd0bc38cabf354e9d2de410
- https://git.kernel.org/stable/c/b5074df412bf3df9d6ce096b6fa03eb1082d05c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49889.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
