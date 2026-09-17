# [M] CVE-2020-6794

## Summary
Severity: Medium
Advisory: CVE-2020-6794
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2020-6794
Type: osv

## Details
If a user saved passwords before Thunderbird 60 and then later set a master password, an unencrypted copy of these passwords is still accessible. This is because the older stored password file was not deleted when the data was copied to a new format starting in Thunderbird 60. The new master password is added only on the new file. This could allow the exposure of stored password data outside of user expectations. This vulnerability affects Thunderbird < 68.5.

## References
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-07/
- https://security.gentoo.org/glsa/202003-10
- https://bugzilla.mozilla.org/show_bug.cgi?id=1606619
