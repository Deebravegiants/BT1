# [M] CVE-2021-20225

## Summary
Severity: Medium
Advisory: CVE-2021-20225
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2021-20225
Type: osv

## Details
A flaw was found in grub2 in versions prior to 2.06. The option parser allows an attacker to write past the end of a heap-allocated buffer by calling certain commands with a large number of specific short forms of options. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWZ36QK4IKU6MWDWNOOWKPH3WXZBHT2R/
- https://security.gentoo.org/glsa/202104-05
- https://security.netapp.com/advisory/ntap-20220325-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1924696
