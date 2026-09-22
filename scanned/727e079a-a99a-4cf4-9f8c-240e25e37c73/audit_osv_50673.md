# [H] CVE-2020-27779

## Summary
Severity: High
Advisory: CVE-2020-27779
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2020-27779
Type: osv

## Details
A flaw was found in grub2 in versions prior to 2.06. The cutmem command does not honor secure boot locking allowing an privileged attacker to remove address ranges from memory creating an opportunity to circumvent SecureBoot protections after proper triage about grub's memory layout. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWZ36QK4IKU6MWDWNOOWKPH3WXZBHT2R/
- https://security.gentoo.org/glsa/202104-05
- https://security.netapp.com/advisory/ntap-20220325-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1900698
