# [H] CVE-2022-29607

## Summary
Severity: High
Advisory: CVE-2022-29607
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-29607
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. Modification of an existing intent to have the same source and destination shows the INSTALLED state without any flow rule. Improper handling of such an intent is misleading to a network operator.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29607.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29607
