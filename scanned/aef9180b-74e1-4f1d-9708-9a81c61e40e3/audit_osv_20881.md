# [M] CVE-2021-3798

## Summary
Severity: Medium
Advisory: CVE-2021-3798
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3798
Type: osv

## Details
A flaw was found in openCryptoki. The openCryptoki Soft token does not check if an EC key is valid when an EC key is created via C_CreateObject, nor when C_DeriveKey is used with ECDH public data. This may allow a malicious user to extract the private key by performing an invalid curve attack.

## References
- https://access.redhat.com/security/cve/CVE-2021-3798
- https://bugzilla.redhat.com/show_bug.cgi?id=1990591
- https://github.com/opencryptoki/opencryptoki/commit/4e3b43c3d8844402c04a66b55c6c940f965109f0
- https://github.com/opencryptoki/opencryptoki/pull/402
