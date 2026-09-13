# [H] Concrete CMS is Vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-prxr-vjgc-2cq9
CVE: CVE-2026-8428
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-prxr-vjgc-2cq9
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below emits a CSRF token in the local_available_update.php view ($token->output('do_update')) but the corresponding do_update() method in concrete/controllers/single_page/dashboard/system/update/update.php never calls $this->token->validate('do_update'). The form is rendered as a POST form, meaning the token reaches the browser, but because the controller discards it without verification, an attacker can craft a cross-site POST that triggers a core CMS update to an attacker-specified version string.  In order to be vulnerable, theictim must be passing canUpgrade()anda valid update version must be present under DIR_CORE_UPDATES.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8428
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
