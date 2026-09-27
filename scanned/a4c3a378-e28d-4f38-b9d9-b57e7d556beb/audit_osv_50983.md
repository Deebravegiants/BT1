# [H] CVE-2020-6796

## Summary
Severity: High
Advisory: CVE-2020-6796
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2020-6796
Type: osv

## Details
A content process could have modified shared memory relating to crash reporting information, crash itself, and cause an out-of-bound write. This could have caused memory corruption and a potentially exploitable crash. This vulnerability affects Firefox < 73 and Firefox < ESR68.5.

## References
- https://usn.ubuntu.com/4278-2/
- https://www.mozilla.org/security/advisories/mfsa2020-05/
- https://www.mozilla.org/security/advisories/mfsa2020-06/
- https://security.gentoo.org/glsa/202003-02
- https://bugzilla.mozilla.org/show_bug.cgi?id=1610426
