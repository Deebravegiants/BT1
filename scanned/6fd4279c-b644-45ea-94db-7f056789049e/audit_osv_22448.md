# [C] CVE-2022-29606

## Summary
Severity: Critical
Advisory: CVE-2022-29606
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-29606
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. An intent with a large port number shows the CORRUPT state, which is misleading to a network operator. Improper handling of such port numbers causes inconsistency between intent and flow rules in the network.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29606.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29606
