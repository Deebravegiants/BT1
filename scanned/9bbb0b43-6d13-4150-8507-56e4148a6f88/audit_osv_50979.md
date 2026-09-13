# [M] CVE-2020-6792

## Summary
Severity: Medium
Advisory: CVE-2020-6792
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2020-6792
Type: osv

## Details
When deriving an identifier for an email message, uninitialized memory was used in addition to the message contents. This vulnerability affects Thunderbird < 68.5.

## References
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1609607
