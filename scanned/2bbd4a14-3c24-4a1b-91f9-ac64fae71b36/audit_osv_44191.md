# [H] Input: synaptics-rmi4 - block s_input when F54 queue is busy

## Summary
Severity: High
Advisory: CVE-2026-80568
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80568
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: synaptics-rmi4 - block s_input when F54 queue is busy

Changing the input (diagnostic report type) mid-stream changes the
report size. Since V4L2 buffers are allocated based on the size at
stream start, changing the input while streaming could lead to a
heap buffer overflow if the new size is larger than the allocated
buffers.

Prevent this by blocking VIDIOC_S_INPUT with -EBUSY if the V4L2 queue
is busy (streaming).

## References
- https://git.kernel.org/stable/c/1d718f1461766e9f00a8dbeb4f13f1b1c19d90ac
- https://git.kernel.org/stable/c/493ba8e794729649689438edba72337111303cc4
- https://git.kernel.org/stable/c/7e994a9ecc0b49ad2fe63da9c92a8aca8a6614af
- https://git.kernel.org/stable/c/cae79513f9115c350561b16f36adcb47c9bfff12
- https://git.kernel.org/stable/c/ddd9a53faf3b65e5920cb802cb1db6f4615bdfef
- https://git.kernel.org/stable/c/fa69f93015becf3729716de2199b58540aa99672
- https://git.kernel.org/stable/c/fbfd76746adc16d64be29ff113f673b70bc3f5c2
- https://git.kernel.org/stable/c/ff0849705d29277fd1f6fc6596674b9308724fb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80568.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
