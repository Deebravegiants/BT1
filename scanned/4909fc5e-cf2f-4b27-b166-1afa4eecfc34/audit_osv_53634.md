# [M] CVE-2023-1018

## Summary
Severity: Medium
Advisory: CVE-2023-1018
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-1018
Type: osv

## Details
An out-of-bounds read vulnerability exists in TPM2.0's Module Library allowing a 2-byte read past the end of a TPM2.0 command in the CryptParameterDecryption routine. An attacker who can successfully exploit this vulnerability can read or access sensitive data stored in the TPM.

## References
- https://www.kb.cert.org/vuls/id/782720
- https://kb.cert.org/vuls/id/782720
- https://trustedcomputinggroup.org/about/security/
- https://trustedcomputinggroup.org/wp-content/uploads/TCGVRT0007-Advisory-FINAL.pdf
