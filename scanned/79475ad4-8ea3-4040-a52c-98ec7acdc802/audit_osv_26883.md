# [H] net: tls: avoid hanging tasks on the tx_lock

## Summary
Severity: High
Advisory: CVE-2023-54306
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54306
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: avoid hanging tasks on the tx_lock

syzbot sent a hung task report and Eric explains that adversarial
receiver may keep RWIN at 0 for a long time, so we are not guaranteed
to make forward progress. Thread which took tx_lock and went to sleep
may not release tx_lock for hours. Use interruptible sleep where
possible and reschedule the work if it can't take the lock.

Testing: existing selftest passes

## References
- https://git.kernel.org/stable/c/1f800f6aae57d2d8f63d32fff383017cbc11cf65
- https://git.kernel.org/stable/c/7123a4337bf73132bbfb5437e4dc83ba864a9a1e
- https://git.kernel.org/stable/c/bde541a57b4204d0a800afbbd3d1c06c9cdb133f
- https://git.kernel.org/stable/c/be5d5d0637fd88c18ee76024bdb22649a1de00d6
- https://git.kernel.org/stable/c/ccf1ccdc5926907befbe880b562b2a4b5f44c087
- https://git.kernel.org/stable/c/f3221361dc85d4de22586ce8441ec2c67b454f5d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54306.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
