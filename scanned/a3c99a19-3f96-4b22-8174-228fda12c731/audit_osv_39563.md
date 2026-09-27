# [H] ALSA: pcm: oss: Fix data race at accessing runtime.oss.trigger

## Summary
Severity: High
Advisory: CVE-2026-46157
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46157
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: oss: Fix data race at accessing runtime.oss.trigger

Currently the runtime.oss.trigger field may be accessed concurrently
without protection, which may lead to the data race.  And, in this
case, it may lead to more severe problem because it's a bit field; as
writing the data, it may overwrite other bit fields as well, which
confuses the operation completely, as spotted by fuzzing.

Fix it by covering runtime.oss.trigger bit fled also with the existing
params_lock mutex in both snd_pcm_oss_get_trigger() and
snd_pcm_oss_poll().

## References
- https://git.kernel.org/stable/c/49f9d048845be874df7997e4b1ce662de450c4b6
- https://git.kernel.org/stable/c/6b01c1bc9a4748ab37548a700a8aaff910e298e6
- https://git.kernel.org/stable/c/901ac0ff15edf9503162e2cf6579bd11a30f1ed4
- https://git.kernel.org/stable/c/ac3e9b55b7da6f0be51720bd330a0edc1a8b61f1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46157.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46157
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
