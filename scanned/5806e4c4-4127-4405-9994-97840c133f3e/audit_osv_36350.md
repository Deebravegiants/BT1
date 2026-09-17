# [H] ALSA: aloop: Fix racy access at PCM trigger

## Summary
Severity: High
Advisory: CVE-2026-23191
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23191
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: aloop: Fix racy access at PCM trigger

The PCM trigger callback of aloop driver tries to check the PCM state
and stop the stream of the tied substream in the corresponding cable.
Since both check and stop operations are performed outside the cable
lock, this may result in UAF when a program attempts to trigger
frequently while opening/closing the tied stream, as spotted by
fuzzers.

For addressing the UAF, this patch changes two things:
- It covers the most of code in loopback_check_format() with
  cable->lock spinlock, and add the proper NULL checks.  This avoids
  already some racy accesses.
- In addition, now we try to check the state of the capture PCM stream
  that may be stopped in this function, which was the major pain point
  leading to UAF.

## References
- https://git.kernel.org/stable/c/5727ccf9d19ca414cb76d9b647883822e2789c2e
- https://git.kernel.org/stable/c/826af7fa62e347464b1b4e0ba2fe19a92438084f
- https://git.kernel.org/stable/c/bad15420050db1803767e58756114800cce91ea4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23191.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23191
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
