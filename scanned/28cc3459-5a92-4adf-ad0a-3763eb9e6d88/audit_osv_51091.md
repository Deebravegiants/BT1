# [H] CVE-2021-20233

## Summary
Severity: High
Advisory: CVE-2021-20233
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2021-20233
Type: osv

## Details
A flaw was found in grub2 in versions prior to 2.06. Setparam_prefix() in the menu rendering code performs a length calculation on the assumption that expressing a quoted single quote will require 3 characters, while it actually requires 4 characters which allows an attacker to corrupt memory by one byte for each quote in the input. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWZ36QK4IKU6MWDWNOOWKPH3WXZBHT2R/
- https://security.netapp.com/advisory/ntap-20220325-0001/
- https://security.gentoo.org/glsa/202104-05
- https://bugzilla.redhat.com/show_bug.cgi?id=1926263
