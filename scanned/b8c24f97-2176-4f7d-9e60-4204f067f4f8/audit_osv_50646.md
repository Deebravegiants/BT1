# [H] CVE-2020-26970

## Summary
Severity: High
Advisory: CVE-2020-26970
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26970
Type: osv

## Details
When reading SMTP server status codes, Thunderbird writes an integer value to a position on the stack that is intended to contain just one byte. Depending on processor architecture and stack layout, this leads to stack corruption that may be exploitable. This vulnerability affects Thunderbird < 78.5.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-53/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1677338
