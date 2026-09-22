# [M] Out-of-Bounds read vulnerability in TCG TPM2.0 reference implementation

## Summary
Severity: Medium
Advisory: CVE-2025-2884
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-06-10
Source: https://osv.dev/vulnerability/CVE-2025-2884
Type: osv

## Details
TCG TPM2.0 Reference implementation's CryptHmacSign helper function is vulnerable to Out-of-Bounds read due to the lack of validation the signature scheme with the signature key's algorithm. See Errata Revision 1.83 and advisory TCGVRT0009 for TCG standard TPM2.0

## References
- https://cert-portal.siemens.com/productcert/html/ssa-628843.html
- https://trustedcomputinggroup.org/about/security/
- https://trustedcomputinggroup.org/wp-content/uploads/TPM2.0-Library-Spec-v1.83-Errata_v1_pub.pdf
- https://trustedcomputinggroup.org/wp-content/uploads/VRT0009-Advisory-FINAL.pdf
- https://www.cve.org/CVERecord?id=CVE-2025-49133
- https://www.kb.cert.org/vuls/id/282450
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2884.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2884
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-01209.html
- https://github.com/stefanberger/libtpms/commit/04b2d8e9afc0a9b6bffe562a23e58c0de11532d1
