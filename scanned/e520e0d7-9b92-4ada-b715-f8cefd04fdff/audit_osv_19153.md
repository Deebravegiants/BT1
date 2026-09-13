# [M] CVE-2020-8236

## Summary
Severity: Medium
Advisory: CVE-2020-8236
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-02
Source: https://osv.dev/vulnerability/CVE-2020-8236
Type: osv

## Details
A wrong configuration in Nextcloud Server 19.0.1 incorrectly made the user feel the passwordless WebAuthn is also a two factor verification by asking for the PIN of the passwordless WebAuthn but not verifying it.

## References
- https://nextcloud.com/security/advisory/?id=NC-SA-2020-037
- https://hackerone.com/reports/924393
