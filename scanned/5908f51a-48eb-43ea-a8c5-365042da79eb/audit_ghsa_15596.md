# [M] Concrete CMS Stored XSS in the "Next&Previous Nav" block

## Summary
Severity: Medium
Advisory: GHSA-xmxj-v2q8-8qx6
CVE: CVE-2024-8661
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-xmxj-v2q8-8qx6
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.19
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.3.4

## Details
Concrete CMS versions 9.0.0 to 9.3.4 and below 8.5.19 are vulnerable to Stored XSS in the "Next&Previous Nav" block. A rogue administrator could add a malicious payload  by executing it in the browsers of targeted users. Since the "Next&Previous Nav" block output was not sufficiently sanitized, the malicious payload could be executed in the browsers of targeted users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8661
- https://github.com/concretecms/concretecms/pull/12204
- https://github.com/concretecms/concretecms/commit/3e548b416ae32efee1e0a42c4510be1106c7eb25
- https://github.com/concretecms/concretecms/commit/ce5ee2ab83fe8de6fa012dd51c5a1dde05cb0dc4
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/934-release-notes
- https://documentation.concretecms.org/developers/introduction/version-history/8519-release-notes
- https://github.com/concretecms/concretecms
