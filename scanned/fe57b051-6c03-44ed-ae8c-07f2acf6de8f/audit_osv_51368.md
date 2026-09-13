# [M] CVE-2021-29969

## Summary
Severity: Medium
Advisory: CVE-2021-29969
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-29969
Type: osv

## Details
If Thunderbird was configured to use STARTTLS for an IMAP connection, and an attacker injected IMAP server responses prior to the completion of the STARTTLS handshake, then Thunderbird didn't ignore the injected data. This could have resulted in Thunderbird showing incorrect information, for example the attacker could have tricked Thunderbird to show folders that didn't exist on the IMAP server. This vulnerability affects Thunderbird < 78.12.

## References
- https://security.gentoo.org/glsa/202208-14
- https://www.mozilla.org/security/advisories/mfsa2021-30/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1682370
