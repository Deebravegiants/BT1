# [M] Xibo CMS Missing Authorization in Module::settingsForm due to PHP operator precedence

## Summary
Severity: Medium
Advisory: CVE-2026-52730
Aliases: GHSA-6h64-j36j-h2v2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-52730
Type: osv

## Details
Xibo is an open source digital signage platform with a web content management system and Windows display player software. Prior to 4.4.3, missing Authorization in Module::settingsForm allows to view (not change) super admin-restricted module settings and leak the full module entity. Exploitation of the vulnerability is possible on behalf of an authorized user who has access to the Module View feature, which are not granted to non-admins as standard. Users should upgrade to version 4.4.3 which fixes this issue. Upgrading to a fixed version is necessary to remediate. Users unable to upgrade should revoke such privileges from users they do not trust.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52730.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-6h64-j36j-h2v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-52730
