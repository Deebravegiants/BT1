# [M] CodiMD - Missing Image Access Controls and Unauthorized Image Access

## Summary
Severity: Medium
Advisory: CVE-2024-38353
Aliases: GHSA-2764-jppc-p2hm
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-38353
Type: osv

## Details
CodiMD allows realtime collaborative markdown notes on all platforms. CodiMD before 2.5.4 is missing authentication and access control vulnerability allowing an unauthenticated attacker to gain unauthorised access to image data uploaded to CodiMD. CodiMD does not require valid authentication to access uploaded images or to upload new image data. An attacker who can determine an uploaded image's URL can gain unauthorised access to uploaded image data. Due to the insecure random filename generation in the underlying Formidable library, an attacker can determine the filenames for previously uploaded images and the likelihood of this issue being exploited is increased. This vulnerability is fixed in 2.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38353.json
- https://github.com/hackmdio/codimd/security/advisories/GHSA-2764-jppc-p2hm
- https://nvd.nist.gov/vuln/detail/CVE-2024-38353
