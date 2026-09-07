# [M] Silverstripe CMS XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gvc8-xjfp-6569
CVE: CVE-2015-8606
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gvc8-xjfp-6569
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=0 <3.1.16
- Packagist: `silverstripe/cms` — affected >=3.2.0 <3.2.1

## Details
Multiple cross-site scripting (XSS) vulnerabilities in SilverStripe CMS & Framework before 3.1.16 and 3.2.0 before 3.2.1 allow remote attackers to inject arbitrary web script or HTML via the (1) Locale or (2) FailedLoginCount parameter to `admin/security/EditForm/field/Members/item/new/ItemEditForm`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8606
- https://cybersecurityworks.com/zerodays/cve-2015-8606-silverstripe.html
- https://github.com/silverstripe/silverstripe-cms
- http://seclists.org/fulldisclosure/2015/Dec/55
- http://www.openwall.com/lists/oss-security/2015/12/17/1
- http://www.openwall.com/lists/oss-security/2015/12/17/11
- http://www.openwall.com/lists/oss-security/2015/12/18/5
- http://www.silverstripe.org/download/security-releases/ss-2015-026
