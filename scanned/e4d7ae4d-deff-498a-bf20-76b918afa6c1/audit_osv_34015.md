# [M] haxcms-nodejs and haxcms-php Improperly Terminate Sessions

## Summary
Severity: Medium
Advisory: CVE-2025-53642
Aliases: GHSA-g4f5-5w5j-p5jg
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-11
Source: https://osv.dev/vulnerability/CVE-2025-53642
Type: osv

## Details
haxcms-nodejs and haxcms-php are backends for HAXcms. The logout function within the application does not terminate a user's session or clear their cookies. Additionally, the application issues a refresh token when logging out. This vulnerability is fixed in 11.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53642.json
- https://github.com/haxtheweb/issues/security/advisories/GHSA-g4f5-5w5j-p5jg
- https://nvd.nist.gov/vuln/detail/CVE-2025-53642
