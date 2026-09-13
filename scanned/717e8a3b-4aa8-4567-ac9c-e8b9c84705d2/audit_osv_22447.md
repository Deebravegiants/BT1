# [H] CVE-2022-29605

## Summary
Severity: High
Advisory: CVE-2022-29605
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-29605
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. IntentManager attempts to install the IPv6 flow rules of an intent into an OpenFlow 1.0 switch that does not support IPv6. Improper handling of the difference in capabilities of the intent and switch is misleading to a network operator.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29605.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29605
