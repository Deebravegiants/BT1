# [M] phpMyFAQ: Public API endpoints expose emails and invisible questions

## Summary
Severity: Medium
Advisory: GHSA-j4rc-96xj-gvqc
CVE: CVE-2026-24422
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-j4rc-96xj-gvqc
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.0.17
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.17

## Details
### Summary
Several public API endpoints return email addresses and non‑public records (e.g. open questions with isVisible=false).

### Details
OpenQuestionController::list() calls Question::getAll() with the default showAll=true, returning invisible questions and their emails. Similar exposures exist in comment/news/faq APIs.

### PoC
```
curl -i -H 'Accept-Language: en' \
  http://192.168.40.16/phpmyfaq/api/v3.0/open-questions
```

### Impact
Privacy exposure of email addresses and non‑public content; increased risk of phishing/scraping.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-j4rc-96xj-gvqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24422
- https://github.com/thorsten/phpMyFAQ
