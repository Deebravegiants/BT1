# [H] ALSA: pcm: Fix races among concurrent hw_params and hw_free calls

## Summary
Severity: High
Advisory: CVE-2022-49291
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49291
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.279, >=4.15.0 <4.19.243, >=4.20.0 <5.4.193, >=5.5.0 <5.10.109, >=5.11.0 <5.15.32, >=5.16.0 <5.16.18, >=5.17.0 <5.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: Fix races among concurrent hw_params and hw_free calls

Currently we have neither proper check nor protection against the
concurrent calls of PCM hw_params and hw_free ioctls, which may result
in a UAF.  Since the existing PCM stream lock can't be used for
protecting the whole ioctl operations, we need a new mutex to protect
those racy calls.

This patch introduced a new mutex, runtime->buffer_mutex, and applies
it to both hw_params and hw_free ioctl code paths.  Along with it, the
both functions are slightly modified (the mmap_count check is moved
into the state-check block) for code simplicity.

## References
- https://git.kernel.org/stable/c/0090c13cbbdffd7da079ac56f80373a9a1be0bf8
- https://git.kernel.org/stable/c/0f6947f5f5208f6ebd4d76a82a4757e2839a23f8
- https://git.kernel.org/stable/c/1bbf82d9f961414d6c76a08f7f843ea068e0ab7b
- https://git.kernel.org/stable/c/33061d0fba51d2bf70a2ef9645f703c33fe8e438
- https://git.kernel.org/stable/c/92ee3c60ec9fe64404dc035e7c41277d74aa26cb
- https://git.kernel.org/stable/c/9cb6c40a6ebe4a0cfc9d6a181958211682cffea9
- https://git.kernel.org/stable/c/a42aa926843acca96c0dfbde2e835b8137f2f092
- https://git.kernel.org/stable/c/fbeb492694ce0441053de57699e1e2b7bc148a69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49291.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49291
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
