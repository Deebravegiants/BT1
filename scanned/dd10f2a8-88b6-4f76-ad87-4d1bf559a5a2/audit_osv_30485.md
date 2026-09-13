# [M] idpf: fix idpf_vc_core_init error path

## Summary
Severity: Medium
Advisory: CVE-2024-53064
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53064
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

idpf: fix idpf_vc_core_init error path

In an event where the platform running the device control plane
is rebooted, reset is detected on the driver. It releases
all the resources and waits for the reset to complete. Once the
reset is done, it tries to build the resources back. At this
time if the device control plane is not yet started, then
the driver timeouts on the virtchnl message and retries to
establish the mailbox again.

In the retry flow, mailbox is deinitialized but the mailbox
workqueue is still alive and polling for the mailbox message.
This results in accessing the released control queue leading to
null-ptr-deref. Fix it by unrolling the work queue cancellation
and mailbox deinitialization in the reverse order which they got
initialized.

## References
- https://git.kernel.org/stable/c/683fcd90ba22507ebeb1921a26dfe77efff8c266
- https://git.kernel.org/stable/c/9b58031ff96b84a38d7b73b23c7ecfb2e0557f43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53064.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53064
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
