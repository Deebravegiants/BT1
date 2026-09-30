# [H] CVE-2021-45100

## Summary
Severity: High
Advisory: CVE-2021-45100
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-45100
Type: osv

## Details
The ksmbd server through 3.4.2, as used in the Linux kernel through 5.15.8, sometimes communicates in cleartext even though encryption has been enabled. This occurs because it sets the SMB2_GLOBAL_CAP_ENCRYPTION flag when using the SMB 3.1.1 protocol, which is a violation of the SMB protocol specification. When Windows 10 detects this protocol violation, it disables encryption.

## References
- https://github.com/cifsd-team/ksmbd/issues/550
- https://marc.info/?l=linux-kernel&m=163961726017023&w=2
- https://security.netapp.com/advisory/ntap-20220107-0001/
- https://github.com/cifsd-team/ksmbd/pull/551
