# [H] firmware: qcom: uefisecapp: Fix memory related IO errors and crashes

## Summary
Severity: High
Advisory: CVE-2024-35994
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35994
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: qcom: uefisecapp: Fix memory related IO errors and crashes

It turns out that while the QSEECOM APP_SEND command has specific fields
for request and response buffers, uefisecapp expects them both to be in
a single memory region. Failure to adhere to this has (so far) resulted
in either no response being written to the response buffer (causing an
EIO to be emitted down the line), the SCM call to fail with EINVAL
(i.e., directly from TZ/firmware), or the device to be hard-reset.

While this issue can be triggered deterministically, in the current form
it seems to happen rather sporadically (which is why it has gone
unnoticed during earlier testing). This is likely due to the two
kzalloc() calls (for request and response) being directly after each
other. Which means that those likely return consecutive regions most of
the time, especially when not much else is going on in the system.

Fix this by allocating a single memory region for both request and
response buffers, properly aligning both structs inside it. This
unfortunately also means that the qcom_scm_qseecom_app_send() interface
needs to be restructured, as it should no longer map the DMA regions
separately. Therefore, move the responsibility of DMA allocation (or
mapping) to the caller.

## References
- https://git.kernel.org/stable/c/dd22b34fb53cb04b13b2f5eee5c9200bb091fc88
- https://git.kernel.org/stable/c/ed09f81eeaa8f9265e1787282cb283f10285c259
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35994.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35994
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
