# [M] CVE-2021-27506

## Summary
Severity: Medium
Advisory: CVE-2021-27506
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/CVE-2021-27506
Type: osv

## Details
The ClamAV Engine (version 0.103.1 and below) component embedded in Storsmshield Network Security (SNS) is subject to DoS in case of parsing of malformed png files. This affect Netasq versions 9.1.0 to 9.1.11 and SNS versions 1.0.0 to 4.2.0. This issue is fixed in SNS 3.7.19, 3.11.7 and 4.2.1.

## References
- https://advisories.stormshield.eu/2021-003/
- https://blog.clamav.net/2021/02/clamav-01031-patch-release.html
