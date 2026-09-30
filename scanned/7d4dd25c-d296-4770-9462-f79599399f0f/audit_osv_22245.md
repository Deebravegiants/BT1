# [M] CVE-2022-24109

## Summary
Severity: Medium
Advisory: CVE-2022-24109
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-24109
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. To attack an intent installed by a normal user, a remote attacker can install a duplicate intent with a different key, and then remove the duplicate one. This will remove the flow rules of the intent, even though the intent still exists in the controller.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24109.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-24109
