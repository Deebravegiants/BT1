# [H] CVE-2018-18513

## Summary
Severity: High
Advisory: CVE-2018-18513
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2018-18513
Type: osv

## Details
A crash can occur when processing a crafted S/MIME message or an XPI package containing a crafted signature. This can be used as a denial-of-service (DOS) attack because Thunderbird reopens the last seen message on restart, triggering the crash again. This vulnerability affects Thunderbird < 60.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1533300
