# [M] CVE-2019-5433

## Summary
Severity: Medium
Advisory: CVE-2019-5433
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2019-05-06
Source: https://osv.dev/vulnerability/CVE-2019-5433
Type: osv

## Details
A user having access to the UI of a Revive Adserver instance could be tricked into clicking on a specifically crafted admin account-switch.php URL that would eventually lead them to another (unsafe) domain, potentially used for stealing credentials or other phishing attacks. This vulnerability was addressed in version 4.2.0.

## References
- https://www.revive-adserver.com/security/revive-sa-2019-001/
- https://hackerone.com/reports/390663
