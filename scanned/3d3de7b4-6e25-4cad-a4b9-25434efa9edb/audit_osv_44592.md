# [M] Craft CMS 5.0.0-RC1 before 5.10.11 File Overwrite via assets/replace-file

## Summary
Severity: Medium
Advisory: CVE-2026-84800
Aliases: GHSA-329j-cx85-8r56
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84800
Type: osv

## Details
Craft CMS versions >= 5.0.0-RC1 and < 5.10.11 contain a missing authorization vulnerability in AssetsController::actionReplaceFile. When a request supplies sourceAssetId and targetFilename but omits assetId, the target asset is resolved by folder and filename after the permission checks execute, so the replacePeerFiles permission is never enforced. An authenticated low-privilege author with only the replaceFiles permission on a shared folder can overwrite the content of a peer's asset file (located in the same folder) with attacker-controlled bytes. Fixed in 5.10.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84800.json
- https://github.com/craftcms/cms/security/advisories/GHSA-329j-cx85-8r56
- https://nvd.nist.gov/vuln/detail/CVE-2026-84800
- https://www.vulncheck.com/advisories/craft-cms-5.0.0-rc1-before-5.10.11-file-overwrite-via-assets-replace-file
