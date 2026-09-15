# [H] ALSA: usb-audio: Add sanity check for OOB writes at silencing

## Summary
Severity: High
Advisory: CVE-2026-43279
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43279
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Add sanity check for OOB writes at silencing

At silencing the playback URB packets in the implicit fb mode before
the actual playback, we blindly assume that the received packets fit
with the buffer size.  But when the setup in the capture stream
differs from the playback stream (e.g. due to the USB core limitation
of max packet size), such an inconsistency may lead to OOB writes to
the buffer, resulting in a crash.

For addressing it, add a sanity check of the transfer buffer size at
prepare_silent_urb(), and stop the data copy if the received data
overflows.  Also, report back the transfer error properly from there,
too.

Note that this doesn't fix the root cause of the playback error
itself, but this merely covers the kernel Oops.

## References
- https://git.kernel.org/stable/c/6af16f1b8649df4c00d6ced924bdd8b72c885b6a
- https://git.kernel.org/stable/c/780dc57794a217b49994fa1d0b42465fb10a00aa
- https://git.kernel.org/stable/c/8995fc0e00b3fee9bf7ecb3d836b635b730c1049
- https://git.kernel.org/stable/c/ccaf9296763be4f76b59e2cac377006016c34435
- https://git.kernel.org/stable/c/fa01973bb79d70c4736b6a4b2de99fbb2cbc8d1f
- https://git.kernel.org/stable/c/fba2105a157fffcf19825e4eea498346738c9948
- https://git.kernel.org/stable/c/fc9e5af60dc199051dc202ae78e1fe76a9977a5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43279.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
