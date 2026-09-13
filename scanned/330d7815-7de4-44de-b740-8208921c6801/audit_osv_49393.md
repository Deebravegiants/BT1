# [C] CVE-2019-11704

## Summary
Severity: Critical
Advisory: CVE-2019-11704
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11704
Type: osv

## Details
A flaw in Thunderbird's implementation of iCal causes a heap buffer overflow in icalmemory_strdup_and_dequote when processing certain email messages, resulting in a potentially exploitable crash. This vulnerability affects Thunderbird < 60.7.1.

## References
- https://security.gentoo.org/glsa/201908-20
- https://www.mozilla.org/security/advisories/mfsa2019-17/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1553814
