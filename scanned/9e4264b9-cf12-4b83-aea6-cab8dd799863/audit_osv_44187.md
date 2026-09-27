# [H] Input: sur40 - fix input device registration ordering

## Summary
Severity: High
Advisory: CVE-2026-80559
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80559
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: sur40 - fix input device registration ordering

In sur40_probe(), input_register_device() was previously called early before
the V4L2 video device and vb2_queue components were fully initialized. If
userspace opened the input device immediately upon registration, sur40_open()
would trigger and start the sur40_poll() worker thread. This worker thread
invokes sur40_process_video() and accesses the uninitialized vb2_queue
structure, leading to a data race and potential system crash.

Furthermore, if V4L2 or video registration failed after input_register_device()
succeeded, the error path fell through to calling input_free_device() on a
successfully registered device instead of input_unregister_device(), corrupting
input core state.

Move input_register_device() to the very end of sur40_probe(). This ensures
the V4L2 and video queue structures are fully initialized before polling can
start, and naturally resolves the error path bug since input_free_device()
is now only called when input registration has not yet occurred.

To maintain strict LIFO (Last-In, First-Out) teardown ordering, also move
input_unregister_device() to the very beginning of sur40_disconnect(). This
guarantees that the input polling worker thread is stopped before V4L2
video components or control handlers are unregistered.

## References
- https://git.kernel.org/stable/c/3e8ed76a4f3572e637653f0654cccdf617903231
- https://git.kernel.org/stable/c/5c1c5227c93f18cd329dd754b4df5e0e2daece1e
- https://git.kernel.org/stable/c/764b507be7b51787e1f577ca3bf0bab7efe81ff8
- https://git.kernel.org/stable/c/83aa12f9f2468a4fbef027c09224dc1011850fb0
- https://git.kernel.org/stable/c/9da976eb649c9e2f588a4499410e4d8af687925f
- https://git.kernel.org/stable/c/beb9b0bd6e6e23f5e9e42b7ef890a50f57f1f3aa
- https://git.kernel.org/stable/c/cd4ecce2fd87760c0ad9a9d28c9fc62ea1dbfd3d
- https://git.kernel.org/stable/c/dab741c9da72102a37cc1020a929051b7c45f9fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80559.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80559
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
