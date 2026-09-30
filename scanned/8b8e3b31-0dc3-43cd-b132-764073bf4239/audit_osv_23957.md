# [H] ALSA: pcm: oss: Fix race at SNDCTL_DSP_SYNC

## Summary
Severity: High
Advisory: CVE-2022-49733
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-02
Source: https://osv.dev/vulnerability/CVE-2022-49733
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.4.215, >=5.5.0 <5.10.148, >=5.11.0 <5.15.68, >=5.16.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: oss: Fix race at SNDCTL_DSP_SYNC

There is a small race window at snd_pcm_oss_sync() that is called from
OSS PCM SNDCTL_DSP_SYNC ioctl; namely the function calls
snd_pcm_oss_make_ready() at first, then takes the params_lock mutex
for the rest.  When the stream is set up again by another thread
between them, it leads to inconsistency, and may result in unexpected
results such as NULL dereference of OSS buffer as a fuzzer spotted
recently.

The fix is simply to cover snd_pcm_oss_make_ready() call into the same
params_lock mutex with snd_pcm_oss_make_ready_locked() variant.

## References
- https://git.kernel.org/stable/c/4051324a6dafd7053c74c475e80b3ba10ae672b0
- https://git.kernel.org/stable/c/723ac5ab2891b6c10dd6cc78ef5456af593490eb
- https://git.kernel.org/stable/c/8015ef9e8a0ee5cecfd0cb6805834d007ab26f86
- https://git.kernel.org/stable/c/8423f0b6d513b259fdab9c9bf4aaa6188d054c2d
- https://git.kernel.org/stable/c/fce793a056c604b41a298317cf704dae255f1b36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49733.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49733
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
