# [M] CVE-2022-29944

## Summary
Severity: Medium
Advisory: CVE-2022-29944
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-29944
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. There is an incorrect comparison of paths installed by intents. An existing intents does not redirect to a new path, even if a new intent that shares the path with higher priority is installed.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29944.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29944
