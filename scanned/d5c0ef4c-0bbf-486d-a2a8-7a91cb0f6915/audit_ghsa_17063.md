# [M] phpMyFAQ Stored HTML Injection at contentLink

## Summary
Severity: Medium
Advisory: GHSA-48vw-jpf8-hwqh
CVE: CVE-2024-28108
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-48vw-jpf8-hwqh
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=3.2.5 <3.2.6

## Details
### Summary
Due to insufficient validation on the `contentLink` parameter, it is possible for unauthenticated users to inject HTML code to the page which might affect other users. _Also, requires that adding new FAQs is allowed for guests and that the admin doesn't check the content of a newly added FAQ._

### PoC
1. Browse to ../phpmyfaq/index.php?action=add&cat=0 , enter `https://test.com?p=<h1>HTML_INJECTION</h1>` for the contentLink parameter.
![image](https://github.com/thorsten/phpMyFAQ/assets/63487456/4925d1ab-aa64-4781-8a44-f4c30cb8499c)

2. Verify the HTML injection by viewing the FAQ itself, “All categories” → “CategoryName” → ”QuestionName”.
![image](https://github.com/thorsten/phpMyFAQ/assets/63487456/54b077d8-fab4-4cb6-870c-f19fc25d8252)

### Impact
Attackers can manipulate the appearance and functionality of web pages by injecting malicious HTML code. This can lead to various undesirable outcomes, such as defacing the website, redirecting users to malicious sites, or altering the content to deceive users. Additionally, unauthenticated HTML injection can compromise user privacy by displaying sensitive information or misleading content. It undermines the integrity of the application and erodes user trust, potentially resulting in loss of reputation and credibility.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-48vw-jpf8-hwqh
- https://nvd.nist.gov/vuln/detail/CVE-2024-28108
- https://github.com/thorsten/phpMyFAQ/commit/4fed1d9602f0635260f789fe85995789d94d6634
- https://github.com/thorsten/phpMyFAQ
