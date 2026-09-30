# [M] CVE-2020-26145

## Summary
Severity: Medium
Advisory: CVE-2020-26145
Aliases: 2860245, 2868035, 2893212, A-177910901, ASB-A-177910901
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2020-26145
Type: osv

## Details
An issue was discovered on Samsung Galaxy S3 i9305 4.4.4 devices. The WEP, WPA, WPA2, and WPA3 implementations accept second (or subsequent) broadcast fragments even when sent in plaintext and process them as full unfragmented frames. An adversary can abuse this to inject arbitrary network packets independent of the network configuration.

## References
- https://github.com/vanhoefm/fragattacks/blob/master/SUMMARY.md
- https://www.fragattacks.com
- http://www.openwall.com/lists/oss-security/2021/05/11/12
- https://cert-portal.siemens.com/productcert/pdf/ssa-913875.pdf
