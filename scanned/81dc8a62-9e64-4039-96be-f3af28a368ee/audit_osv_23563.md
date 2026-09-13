# [H] mt76: mt7921: fix crash when startup fails.

## Summary
Severity: High
Advisory: CVE-2022-49129
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49129
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7921: fix crash when startup fails.

If the nic fails to start, it is possible that the
reset_work has already been scheduled.  Ensure the
work item is canceled so we do not have use-after-free
crash in case cleanup is called before the work item
is executed.

This fixes crash on my x86_64 apu2 when mt7921k radio
fails to work.  Radio still fails, but OS does not
crash.

## References
- https://git.kernel.org/stable/c/38fbe806645090c07aa97171f20fc62c3d7d3a98
- https://git.kernel.org/stable/c/827e7799c61b978fbc2cc9dac66cb62401b2b3f0
- https://git.kernel.org/stable/c/ac1260b661c2ef0d0a56680cdb5672b931b7be8f
- https://git.kernel.org/stable/c/c1a5e6002ec441a3b9fb4d048b4b49ae93409a46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49129.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
