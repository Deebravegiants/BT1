# [H] CVE-2016-0780

## Summary
Severity: High
Advisory: CVE-2016-0780
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-25
Source: https://osv.dev/vulnerability/CVE-2016-0780
Type: osv

## Details
It was discovered that cf-release v231 and lower, Pivotal Cloud Foundry Elastic Runtime 1.5.x versions prior to 1.5.17 and Pivotal Cloud Foundry Elastic Runtime 1.6.x versions prior to 1.6.18 do not properly enforce disk quotas in certain cases. An attacker could use an improper disk quota value to bypass enforcement and consume all the disk on DEAs/CELLs causing a potential denial of service for other applications.

## References
- https://pivotal.io/security/cve-2016-0780
