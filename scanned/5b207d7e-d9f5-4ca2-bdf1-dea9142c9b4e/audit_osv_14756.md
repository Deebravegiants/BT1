# [H] CVE-2019-11283

## Summary
Severity: High
Advisory: CVE-2019-11283
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-11283
Type: osv

## Details
Cloud Foundry SMB Volume, versions prior to v2.0.3, accidentally outputs sensitive information to the logs. A remote user with access to the SMB Volume logs can discover the username and password for volumes that have been recently created, allowing the user to take control of the SMB Volume.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11283
