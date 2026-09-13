# [H] USB: serial: digi_acceleport: fix write buffer corruption

## Summary
Severity: High
Advisory: CVE-2026-64333
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64333
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: serial: digi_acceleport: fix write buffer corruption

The digi_write_inb_command() is supposed to wait for the write urb to
become available or return an error, but instead it updates the transfer
buffer and tries to resubmit the urb on timeout.

To make things worse, for commands like break control where no timeout
is used, the driver would corrupt the urb immediately due to a broken
jiffies comparison (on 32-bit machines this takes five minutes of uptime
to trigger due to INITIAL_JIFFIES).

Fix this by adding the missing return on timeout and waiting
indefinitely when no timeout has been specified as intended.

This issue was (sort of) flagged by Sashiko when reviewing an unrelated
change to the driver.

## References
- https://git.kernel.org/stable/c/1243f120790042c2ac92e84e797dacc75fff4366
- https://git.kernel.org/stable/c/24ca1fea8f2753bf33e1d458ec1ae5d9b7796a65
- https://git.kernel.org/stable/c/2f296974acc279f05f284441bfe3064074958d11
- https://git.kernel.org/stable/c/5d9dc88bdf8897788b0eed57113e9eca7fd42ea9
- https://git.kernel.org/stable/c/699dfb6917503b3cda4d5da6941cf79c3c1b4c8b
- https://git.kernel.org/stable/c/a274b3794fe1852c3d9fe6d900b94053c0b03410
- https://git.kernel.org/stable/c/a3a13fdc53103b07335918e2cdeb465038a71725
- https://git.kernel.org/stable/c/e60e4873e9178da9f4f2674e4c2ff085d5a84f79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64333.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64333
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
