# [M] CVE-2021-40327

## Summary
Severity: Medium
Advisory: CVE-2021-40327
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40327
Type: osv

## Details
Trusted Firmware-M (TF-M) 1.4.0, when Profile Small is used, has incorrect access control. NSPE can access a secure key (held by the Crypto service) based solely on knowledge of its key ID. For example, there is no authorization check associated with the relationship between a caller and a key owner.

## References
- https://developer.arm.com/support/arm-security-updates
- https://git.trustedfirmware.org/TF-M/trusted-firmware-m.git/
- https://tf-m-user-guide.trustedfirmware.org/docs/security/security_advisories/profile_small_key_id_encoding_vulnerability.html
