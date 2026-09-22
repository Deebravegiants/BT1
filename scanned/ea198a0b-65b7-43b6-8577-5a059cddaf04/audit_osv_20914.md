# [M] CVE-2021-38364

## Summary
Severity: Medium
Advisory: CVE-2021-38364
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2021-38364
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. There is an incorrect comparison of flow rules installed by intents. A remote attacker can install or remove a new intent, and consequently modify or delete the existing flow rules related to other intents.

## References
- https://opennetworking.org/onos/
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
