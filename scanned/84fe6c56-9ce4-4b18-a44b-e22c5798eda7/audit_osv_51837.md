# [H] CVE-2021-4202

## Summary
Severity: High
Advisory: CVE-2021-4202
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-4202
Type: osv

## Details
A use-after-free flaw was found in nci_request in net/nfc/nci/core.c in NFC Controller Interface (NCI) in the Linux kernel. This flaw could allow a local attacker with user privileges to cause a data race problem while the device is getting removed, leading to a privilege escalation problem.

## References
- https://security.netapp.com/advisory/ntap-20220513-0002/
- http://www.openwall.com/lists/oss-security/2022/06/01/2
- http://www.openwall.com/lists/oss-security/2022/06/04/2
- http://www.openwall.com/lists/oss-security/2022/06/07/2
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=3e3b5dfcd16a3e254aab61bd1e8c417dd4503102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=48b71a9e66c2eab60564b1b1c85f4928ed04e406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=86cdf8e38792545161dbe3350a7eced558ba4d15
- https://bugzilla.redhat.com/show_bug.cgi?id=2036682
