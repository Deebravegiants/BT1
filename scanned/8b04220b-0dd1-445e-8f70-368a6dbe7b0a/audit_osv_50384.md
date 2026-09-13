# [H] CVE-2020-14372

## Summary
Severity: High
Advisory: CVE-2020-14372
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2020-14372
Type: osv

## Details
A flaw was found in grub2 in versions prior to 2.06, where it incorrectly enables the usage of the ACPI command when Secure Boot is enabled. This flaw allows an attacker with privileged access to craft a Secondary System Description Table (SSDT) containing code to overwrite the Linux kernel lockdown variable content directly into memory. The table is further loaded and executed by the kernel, defeating its Secure Boot lockdown and allowing the attacker to load unsigned code. The highest threat from this vulnerability is to data confidentiality and integrity, as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWZ36QK4IKU6MWDWNOOWKPH3WXZBHT2R/
- https://security.gentoo.org/glsa/202104-05
- https://security.netapp.com/advisory/ntap-20210416-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=1873150
- https://access.redhat.com/security/vulnerabilities/RHSB-2021-003
