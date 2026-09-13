# [M] CVE-2022-29609

## Summary
Severity: Medium
Advisory: CVE-2022-29609
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-29609
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. An intent with the same source and destination shows the INSTALLING state, indicating that its flow rules are installing. Improper handling of such an intent is misleading to a network operator.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29609.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29609
