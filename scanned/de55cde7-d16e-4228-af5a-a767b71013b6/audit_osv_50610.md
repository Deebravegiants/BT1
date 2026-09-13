# [H] CVE-2020-25647

## Summary
Severity: High
Advisory: CVE-2020-25647
CVSS: 7.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2020-25647
Type: osv

## Details
A flaw was found in grub2 in versions prior to 2.06. During USB device initialization, descriptors are read with very little bounds checking and assumes the USB device is providing sane values. If properly exploited, an attacker could trigger memory corruption leading to arbitrary code execution allowing a bypass of the Secure Boot mechanism. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWZ36QK4IKU6MWDWNOOWKPH3WXZBHT2R/
- https://security.gentoo.org/glsa/202104-05
- https://security.netapp.com/advisory/ntap-20220325-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1886936
