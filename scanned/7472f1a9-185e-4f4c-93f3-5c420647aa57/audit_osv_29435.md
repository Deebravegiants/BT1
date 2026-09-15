# [M] Improper Neutralization of Delimiters in Mongoose Web Server library

## Summary
Severity: Medium
Advisory: CVE-2024-42385
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-42385
Type: osv

## Details
Improper Neutralization of Delimiters vulnerability in Cesanta Mongoose Web Server v7.14 allows to trigger an out-of-bound memory write if the PEM certificate contains unexpected characters.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-142885.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42385.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42385
- https://www.nozominetworks.com/labs/vulnerability-advisories-cve-2024-42385
- https://github.com/cesanta/mongoose
