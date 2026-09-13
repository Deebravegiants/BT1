# [H] CVE-2023-1017

## Summary
Severity: High
Advisory: CVE-2023-1017
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-1017
Type: osv

## Details
An out-of-bounds write vulnerability exists in TPM2.0's Module Library allowing writing of a 2-byte data past the end of TPM2.0 command in the CryptParameterDecryption routine. An attacker who can successfully exploit this vulnerability can lead to denial of service (crashing the TPM chip/process or rendering it unusable) and/or arbitrary code execution in the TPM context.

## References
- https://www.kb.cert.org/vuls/id/782720
- https://kb.cert.org/vuls/id/782720
- https://trustedcomputinggroup.org/about/security/
- https://trustedcomputinggroup.org/wp-content/uploads/TCGVRT0007-Advisory-FINAL.pdf
