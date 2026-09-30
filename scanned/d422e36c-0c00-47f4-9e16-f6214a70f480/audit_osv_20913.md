# [H] CVE-2021-38363

## Summary
Severity: High
Advisory: CVE-2021-38363
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2021-38363
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. In IntentManager, the install-requested intent (which causes an exception) remains in pendingMap (in memory) forever. Deletion is possible neither by a user nor by the intermittent Intent Cleanup process.

## References
- https://opennetworking.org/onos/
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
