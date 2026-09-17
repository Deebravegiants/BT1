# [M] CVE-2021-25220

## Summary
Severity: Medium
Advisory: CVE-2021-25220
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-25220
Type: osv

## Details
BIND 9.11.0 -> 9.11.36 9.12.0 -> 9.16.26 9.17.0 -> 9.18.0 BIND Supported Preview Editions: 9.11.4-S1 -> 9.11.36-S1 9.16.8-S1 -> 9.16.26-S1 Versions of BIND 9 earlier than those shown - back to 9.1.0, including Supported Preview Editions - are also believed to be affected but have not been tested as they are EOL. The cache could become poisoned with incorrect records leading to queries being made to the wrong servers, which might also result in false information being returned to clients.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2SXT7247QTKNBQ67MNRGZD23ADXU6E5U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5VX3I2U3ICOIEI5Y7OYA6CHOLFMNH3YQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/API7U5E7SX7BAAVFNW366FFJGD6NZZKV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DE3UAVCPUMAKG27ZL5YXSP2C3RIOW3JZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NYD7US4HZRFUGAJ66ZTHFBYVP5N3OQBY/
- https://supportportal.juniper.net/s/article/2022-10-Security-Bulletin-Junos-OS-SRX-Series-Cache-poisoning-vulnerability-in-BIND-used-by-DNS-Proxy-CVE-2021-25220?language=en_US
- https://kb.isc.org/v1/docs/cve-2021-25220
- https://security.gentoo.org/glsa/202210-25
- https://security.netapp.com/advisory/ntap-20220408-0001/
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
