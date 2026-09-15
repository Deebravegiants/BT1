# [H] CVE-2019-16058

## Summary
Severity: High
Advisory: CVE-2019-16058
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-16058
Type: osv

## Details
An issue was discovered in the pam_p11 component 0.2.0 and 0.3.0 for OpenSC. If a smart card creates a signature with a length longer than 256 bytes, this triggers a buffer overflow. This may be the case for RSA keys with 4096 bits depending on the signature scheme.

## References
- http://www.openwall.com/lists/oss-security/2019/09/12/1
- https://github.com/OpenSC/pam_p11/commit/d150b60e1e14c261b113f55681419ad1dfa8a76c
