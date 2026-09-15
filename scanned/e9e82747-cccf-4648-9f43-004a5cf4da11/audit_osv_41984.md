# [H] fuse-uring: make a fuse_req on SQE commit only findable after memcpy

## Summary
Severity: High
Advisory: CVE-2026-64259
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64259
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse-uring: make a fuse_req on SQE commit only findable after memcpy

Bad userspace might try to trick us and send commit SQEs request
unique / commit-id of requests that are not even send to
fuse-server (io_uring_cmd_done() not called) yet.

fuse_uring_commit_fetch() ends the fuse request when the ring entry
has a wrong state, but that could have caused a use-after-free
with the memcpy operations in fuse_uring_send_in_task().
In order to avoid such races the call of fuse_uring_add_to_pq()
is moved after the copy operations and just before completing
the io-uring request - malicious userspace cannot find the request
anymore until all prepration work in fuse-client/kernel is completed.

This also moves fuse_uring_add_to_pq() a bit up in the code to
avoid a forward declaration. Also not with a preparation commit,
to make it easier to back port to older kernels.

## References
- https://git.kernel.org/stable/c/1efd3d474fc0ba74dfd984249bca78807d739812
- https://git.kernel.org/stable/c/a635f427d57e2012102ae4886b48d8955c59fb86
- https://git.kernel.org/stable/c/e1711479e9068ea31b31353a702a51e639c3d059
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64259.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64259
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
