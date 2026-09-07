# [M] Concrete5 CMS contains an XPath injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r7vr-wg3f-8hr9
CVE: CVE-2022-50807
CWE: CWE-643
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-r7vr-wg3f-8hr9
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected 9.1.3

## Details
Concrete5 CMS version 9.1.3 contains an XPath injection vulnerability that allows attackers to manipulate URL path parameters with malicious payloads. Attackers can flood the system with crafted requests to potentially extract internal content paths and system information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-50807
- https://github.com/concretecms/concretecms
- https://github.com/nu11secur1ty/CVE-nu11secur1ty/tree/main/vendors/concretecms.org/2022/concretecms-9.1.3
- https://www.concretecms.org
- https://www.concretecms.org/download
- https://www.exploit-db.com/exploits/51144
- https://www.vulncheck.com/advisories/concrete-cme-xpath-injection
