# [H] Concrete CMS 9 through 9.5.2 is vulnerable to Missing Authorization in the orphaned-block alias route, allowing an authenticated editor to disclose and force-delete arbitrary blocks

## Summary
Severity: High
Advisory: CVE-2026-81909
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-81909
Type: osv

## Details
Concrete CMS 9 through 9.5.2 is vulnerable to Missing Authorization in the block alias route (Process::alias() in concrete/controllers/backend/block/process.php).It does not verify that the referenced block is genuinely orphaned on the target page, nor that the caller holds any permission over the source block. A user granted only an area-scoped add_block_to_area delegation on their own page can therefore pass any block ID on the site: the source block's content is duplicated into an area the rogue editor controls, disclosing that content, and the original block is then force-deleted in the same request, destroying arbitrary site content. The Concrete CMS security team gave this vulnerability a CVSS v4.0 score of 5.9 with vector CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N. Thanks Yonatan Drori from Tenzai for reporting.

## References
- https://documentation.concretecms.org/developers/introduction/version-history/953-release-notes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81909.json
- https://github.com/concretecms/concretecms
- https://nvd.nist.gov/vuln/detail/CVE-2026-81909
