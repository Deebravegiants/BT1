# [M] phpMyFAQ Vulnerable to Stored HTML Injection at FAQ

## Summary
Severity: Medium
Advisory: GHSA-ww33-jppq-qfrp
CVE: CVE-2024-56199
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2025-01-02
Source: https://github.com/advisories/GHSA-ww33-jppq-qfrp
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=3.2.10
- Packagist: `thorsten/phpmyfaq` — affected >=3.2.10

## Details
### Summary
Due to insufficient validation on the content of new FAQ posts, it is possible for authenticated users to inject malicious HTML or JavaScript code that can impact other users viewing the FAQ. This vulnerability arises when user-provided inputs in FAQ entries are not sanitized or escaped before being rendered on the page.

### Details
An attacker can inject malicious HTML content into the FAQ editor at http://localhost/admin/index.php?action=editentry, resulting in a complete disruption of the FAQ page's user interface. By injecting malformed HTML elements styled to cover the entire screen, an attacker can render the page unusable. This injection manipulates the page structure by introducing overlapping buttons, images, and iframes, breaking the intended layout and functionality. 

### PoC

1. In the source code of a FAQ Q&A post, insert the likes of this snippet:
```
<p>&lt;--`<img src="&#96;"> --!&gt;</p>
<div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"><form><button>HTML INJECTION 1<img> <img> <img> <img> <iframe></iframe></button>
<div style="xg-p: absolute; top: 0; left: 0; width: 100%; height: 100%;">x</div>
<button>HTML INJECTION 2<iframe></iframe> <iframe></iframe> </button></form></div>
```

![image](https://github.com/user-attachments/assets/7c12ff40-1978-4dee-b501-c48f3ea2b9ba)
2. A normal user would see the broken FAQ page, or otherwise manipulated by the attacker to present a different malicious page:
![image](https://github.com/user-attachments/assets/4b815663-4836-4370-8b02-5b01bce71b0c)
 
A demo (fresh install overwrites every 24hours) here: https://roy.demo.phpmyfaq.de/content/1/24/en/24.html?

### Impact
Exploiting this issue can lead to Denial of Service for legitimate users, damage to the user experience, and potential abuse in phishing or defacement attacks.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-ww33-jppq-qfrp
- https://nvd.nist.gov/vuln/detail/CVE-2024-56199
- https://github.com/thorsten/phpMyFAQ
