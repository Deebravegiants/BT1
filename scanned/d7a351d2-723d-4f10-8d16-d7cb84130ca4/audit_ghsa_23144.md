# [M] Shopware XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mvrx-cmqw-2jgj
CVE: CVE-2017-15374
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mvrx-cmqw-2jgj
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.2.5

## Details
Shopware v5.2.5 - v5.3 is vulnerable to cross site scripting in the customer and order section of the content management system backend modules. Remote attackers are able to inject malicious script code into the firstname, lastname, or order input fields to provoke persistent execution in the customer and orders section of the backend. The execution occurs in the administrator backend listing when processing a preview of the customers (kunden) or orders (bestellungen). The injection can be performed interactively via user registration or by manipulation of the order information inputs. The issue can be exploited by low privileged user accounts against higher privileged (admin or moderator) accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15374
- https://www.exploit-db.com/exploits/43849
- https://www.vulnerability-lab.com/get_content.php?id=1922
