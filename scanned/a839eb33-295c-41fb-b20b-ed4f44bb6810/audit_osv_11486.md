# [H] CVE-2017-8037

## Summary
Severity: High
Advisory: CVE-2017-8037
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-21
Source: https://osv.dev/vulnerability/CVE-2017-8037
Type: osv

## Details
In Cloud Foundry Foundation CAPI-release versions after v1.6.0 and prior to v1.38.0 and cf-release versions after v244 and prior to v270, there is an incomplete fix for CVE-2017-8035. If you took steps to remediate CVE-2017-8035 you should also upgrade to fix this CVE. A carefully crafted CAPI request from a Space Developer can allow them to gain access to files on the Cloud Controller VM for that installation, aka an Information Leak / Disclosure.

## References
- http://www.securityfocus.com/bid/100448
- https://www.cloudfoundry.org/cve-2017-8037/
