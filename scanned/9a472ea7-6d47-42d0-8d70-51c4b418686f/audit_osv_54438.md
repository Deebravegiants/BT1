# [M] CVE-2023-6240

## Summary
Severity: Medium
Advisory: CVE-2023-6240
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-02-04
Source: https://osv.dev/vulnerability/CVE-2023-6240
Type: osv

## Details
A Marvin vulnerability side-channel leakage was found in the RSA decryption operation in the Linux Kernel. This issue may allow a network attacker to decrypt ciphertexts or forge signatures, limiting the services that use that private key.

## References
- https://access.redhat.com/errata/RHSA-2024:2758
- https://access.redhat.com/errata/RHSA-2024:3421
- https://access.redhat.com/errata/RHSA-2024:3627
- https://access.redhat.com/security/cve/CVE-2023-6240
- https://people.redhat.com/~hkario/marvin/
- https://access.redhat.com/errata/RHSA-2024:1881
- https://access.redhat.com/errata/RHSA-2024:1882
- https://access.redhat.com/errata/RHSA-2024:3414
- https://access.redhat.com/errata/RHSA-2024:3618
- https://security.netapp.com/advisory/ntap-20240628-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2250843
- https://securitypitfalls.wordpress.com/2023/10/16/experiment-with-side-channel-attacks-yourself/
