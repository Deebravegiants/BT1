# [C] Craft CMS before 5.10.12 Remote Code Execution via element-index

## Summary
Severity: Critical
Advisory: CVE-2026-86732
Aliases: GHSA-9wcj-wqqh-cqvg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86732
Type: osv

## Details
Craft CMS versions before 5.10.12 contain a remote code execution vulnerability in the element-index endpoint that allows authenticated content editors to instantiate arbitrary classes through the criteria parameter. Attackers can inject a malicious class via criteria[withTransforms][0][class] that reaches ImageTransforms::normalizeTransform(), then use a PHP gadget chain with yii\rbac\PhpManager to execute code by pointing itemFile to a request log containing PHP payload in the User-Agent header.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86732.json
- https://github.com/craftcms/cms/security/advisories/GHSA-9wcj-wqqh-cqvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-86732
- https://www.vulncheck.com/advisories/craft-cms-before-5.10.12-remote-code-execution-via-element-index
