# [H] CVE-2019-3787

## Summary
Severity: High
Advisory: CVE-2019-3787
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-3787
Type: osv

## Details
Cloud Foundry UAA, versions prior to 73.0.0, falls back to appending “unknown.org” to a user's email address when one is not provided and the user name does not contain an @ character. This domain is held by a private company, which leads to attack vectors including password recovery emails sent to a potentially fraudulent address. This would allow the attacker to gain complete control of the user's account.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3787
