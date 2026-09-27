# [M] CVE-2021-4122

## Summary
Severity: Medium
Advisory: CVE-2021-4122
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4122
Type: osv

## Details
It was found that a specially crafted LUKS header could trick cryptsetup into disabling encryption during the recovery of the device. An attacker with physical access to the medium, such as a flash disk, could use this flaw to force a user into permanently disabling the encryption layer of that medium.

## References
- https://access.redhat.com/security/cve/CVE-2021-4122
- https://mirrors.edge.kernel.org/pub/linux/utils/cryptsetup/v2.4/v2.4.3-ReleaseNotes
- https://bugzilla.redhat.com/show_bug.cgi?id=2031859
- https://bugzilla.redhat.com/show_bug.cgi?id=2032401
- https://gitlab.com/cryptsetup/cryptsetup/-/commit/0113ac2d889c5322659ad0596d4cfc6da53e356c
