# [H] CVE-2017-12169

## Summary
Severity: High
Advisory: CVE-2017-12169
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-10
Source: https://osv.dev/vulnerability/CVE-2017-12169
Type: osv

## Details
It was found that FreeIPA 4.2.0 and later could disclose password hashes to users having the 'System: Read Stage Users' permission. A remote, authenticated attacker could potentially use this flaw to disclose the password hashes belonging to Stage Users. This security issue does not result in disclosure of password hashes belonging to active standard users. NOTE: some developers feel that this report is a suggestion for a design change to Stage User activation, not a statement of a vulnerability.

## References
- http://www.securityfocus.com/bid/102136
- https://bugzilla.redhat.com/show_bug.cgi?id=1487697
