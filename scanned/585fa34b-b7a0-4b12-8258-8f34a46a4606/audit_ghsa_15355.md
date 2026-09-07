# [M] Khoj Vulnerable to Stored Cross-site Scripting In Automate (Preview feature)

## Summary
Severity: Medium
Advisory: GHSA-cf72-vg59-4j4h
CVE: CVE-2024-43396
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-cf72-vg59-4j4h
Type: github-advisory

## Affected
- PyPI: `khoj` — affected >=0 <1.15.0

## Details
### Summary
The Automation feature allows a user to insert arbitrary HTML inside the task instructions, resulting in a Stored XSS. 

### Details
The `q` parameter for the `/api/automation` endpoint does not get correctly sanitized when rendered on the page, resulting in the ability of users to inject arbitrary HTML/JS.

### PoC
```
POST /api/automation?q=%22%3E%3C%2Ftextarea%3E%3Cimg%20src%3Dx%20onerror%3Dalert(document.cookie)%3E%3Cscript%3Ealert(2)%3C%2Fscript%3E
```

### Impact
Stored XSS:
![image](https://github.com/khoj-ai/khoj/assets/115566010/6b5b9f60-e05c-448b-82b4-bf010ad8a4f0)

### Fix
- Added a Content Security Policy to all config pages on the web client, including the automation page
- Used DOM scripting to construct all components on the config pages, including the automation page

## References
- https://github.com/khoj-ai/khoj/security/advisories/GHSA-cf72-vg59-4j4h
- https://nvd.nist.gov/vuln/detail/CVE-2024-43396
- https://github.com/khoj-ai/khoj/commit/1c7a562880eeb7354325545d2cf6c5d1d1134812
- https://github.com/khoj-ai/khoj/commit/55be90cdd2f9d6a09c8bf9ceea52fc36b9201626
- https://github.com/khoj-ai/khoj
