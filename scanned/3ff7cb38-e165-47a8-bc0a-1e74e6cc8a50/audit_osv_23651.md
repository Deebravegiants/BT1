# [H] ALSA: oss: Fix PCM OSS buffer allocation overflow

## Summary
Severity: High
Advisory: CVE-2022-49292
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49292
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.237, >=4.20.0 <5.4.188, >=5.5.0 <5.10.109, >=5.11.0 <5.15.32, >=5.16.0 <5.16.18, >=5.17.0 <5.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: oss: Fix PCM OSS buffer allocation overflow

We've got syzbot reports hitting INT_MAX overflow at vmalloc()
allocation that is called from snd_pcm_plug_alloc().  Although we
apply the restrictions to input parameters, it's based only on the
hw_params of the underlying PCM device.  Since the PCM OSS layer
allocates a temporary buffer for the data conversion, the size may
become unexpectedly large when more channels or higher rates is given;
in the reported case, it went over INT_MAX, hence it hits WARN_ON().

This patch is an attempt to avoid such an overflow and an allocation
for too large buffers.  First off, it adds the limit of 1MB as the
upper bound for period bytes.  This must be large enough for all use
cases, and we really don't want to handle a larger temporary buffer
than this size.  The size check is performed at two places, where the
original period bytes is calculated and where the plugin buffer size
is calculated.

In addition, the driver uses array_size() and array3_size() for
multiplications to catch overflows for the converted period size and
buffer bytes.

## References
- https://git.kernel.org/stable/c/0c4190b41a69990666b4000999e27f8f1b2a426b
- https://git.kernel.org/stable/c/5ce74ff7059341d8b2f4d01c3383491df63d1898
- https://git.kernel.org/stable/c/7a40cbf3579a8e14849ba7ce46309c1992658d2b
- https://git.kernel.org/stable/c/a63af1baf0a5e11827db60e3127f87e437cab6e5
- https://git.kernel.org/stable/c/e74a069c6a7bb505f3ade141dddf85f4b0b5145a
- https://git.kernel.org/stable/c/efb6402c3c4a7c26d97c92d70186424097b6e366
- https://git.kernel.org/stable/c/fb08bf99195a87c798bc8ae1357337a981faeade
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49292.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
