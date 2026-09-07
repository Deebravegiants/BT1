# [M] Apereo CAS has inefficient regular expression complexity

## Summary
Severity: Medium
Advisory: GHSA-8rx4-fxq5-vj4v
CVE: CVE-2025-3985
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-04-27
Source: https://github.com/advisories/GHSA-8rx4-fxq5-vj4v
Type: github-advisory

## Affected
- Maven: `org.apereo.cas:cas-management-webapp-support` — affected >=0

## Details
A vulnerability was found in Apereo CAS 5.2.6. It has been classified as problematic. This affects the function ResponseEntity of the file cas-5.2.6\webapp-mgmt\cas-management-webapp-support\src\main\java\org\apereo\cas\mgmt\services\web\ManageRegisteredServicesMultiActionController.java. The manipulation of the argument Query leads to inefficient regular expression complexity. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3985
- https://github.com/apereo/cas
- https://vuldb.com/?ctiid.306321
- https://vuldb.com/?id.306321
- https://vuldb.com/?submit.557110
- https://wx.mail.qq.com/s?k=lzDuxVkSRXUZ0bwZEG
