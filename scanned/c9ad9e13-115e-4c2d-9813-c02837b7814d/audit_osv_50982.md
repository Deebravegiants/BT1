# [M] CVE-2020-6795

## Summary
Severity: Medium
Advisory: CVE-2020-6795
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2020-6795
Type: osv

## Details
When processing a message that contains multiple S/MIME signatures, a bug in the MIME processing code caused a null pointer dereference, leading to an unexploitable crash. This vulnerability affects Thunderbird < 68.5.

## References
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://security.gentoo.org/glsa/202003-10
- https://www.mozilla.org/security/advisories/mfsa2020-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1611105
