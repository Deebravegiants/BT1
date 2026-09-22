# [M] CVE-2018-7174

## Summary
Severity: Medium
Advisory: CVE-2018-7174
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-15
Source: https://osv.dev/vulnerability/CVE-2018-7174
Type: osv

## Details
An issue was discovered in xpdf 4.00. An infinite loop in XRef::Xref allows an attacker to cause denial of service because loop detection exists only for tables, not streams.

## References
- https://forum.xpdfreader.com/viewtopic.php?f=3&t=605
