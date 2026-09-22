# [H] CVE-2020-12398

## Summary
Severity: High
Advisory: CVE-2020-12398
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12398
Type: osv

## Details
If Thunderbird is configured to use STARTTLS for an IMAP server, and the server sends a PREAUTH response, then Thunderbird will continue with an unencrypted connection, causing email data to be sent without protection. This vulnerability affects Thunderbird < 68.9.0.

## References
- https://usn.ubuntu.com/4421-1/
- https://www.mozilla.org/security/advisories/mfsa2020-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1613623
