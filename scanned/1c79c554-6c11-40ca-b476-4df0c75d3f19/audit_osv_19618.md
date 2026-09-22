# [C] CVE-2021-22915

## Summary
Severity: Critical
Advisory: CVE-2021-22915
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-11
Source: https://osv.dev/vulnerability/CVE-2021-22915
Type: osv

## Details
Nextcloud server before 19.0.11, 20.0.10, 21.0.2 is vulnerable to brute force attacks due to lack of inclusion of IPv6 subnets in rate-limiting considerations. This could potentially result in an attacker bypassing rate-limit controls such as the Nextcloud brute-force protection.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AGXGR6HYGQ6MZXISMJEHCOXRGRFRUFMA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L6BO6P6MP2MOWA6PZRXX32PLWPXN5O4S/
- https://nextcloud.com/security/advisory/?id=NC-SA-2021-009
- https://hackerone.com/reports/1154003
