# [M] TinyScientist has Path Traversal Vulnerability in PDF Review Function (CWE-22)

## Summary
Severity: Medium
Advisory: GHSA-rrgf-hcr9-jq6h
CVE: CVE-2025-55149
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-11
Source: https://github.com/advisories/GHSA-rrgf-hcr9-jq6h
Type: github-advisory

## Affected
- PyPI: `tiny-scientist` — affected >=0

## Details
## Description
A critical path traversal vulnerability (CWE-22) has been identified in the `review_paper` function in `backend/app.py`. The vulnerability allows malicious users to access arbitrary PDF files on the server by providing crafted file paths that bypass the intended security restrictions.

## Impact
This vulnerability allows attackers to:
- Read any PDF file accessible to the server process
- Potentially access sensitive documents outside the intended directory
- Perform reconnaissance on the server's file system structure

## Vulnerable Code
The issue occurs in the `review_paper` function around line 744:

```python
if pdf_path.startswith("/api/files/"):
    # Safe path handling for API routes
    relative_path = pdf_path[len("/api/files/"):]
    generated_base = os.path.join(project_root, "generated")
    absolute_pdf_path = os.path.join(generated_base, relative_path)
else:
    absolute_pdf_path = pdf_path  # VULNERABLE: Direct use of user input
```

## Proof of Concept
```bash
curl -X POST http://localhost:5000/api/review \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "/etc/passwd"}'
```

## Credit
This vulnerability was discovered and reported by Ruizhe.

## References
- https://github.com/ulab-uiuc/tiny-scientist/security/advisories/GHSA-rrgf-hcr9-jq6h
- https://nvd.nist.gov/vuln/detail/CVE-2025-55149
- https://github.com/ulab-uiuc/tiny-scientist/commit/7fd42873603012acb8c55a4fc3eaac9ab18e6559
- https://github.com/ulab-uiuc/tiny-scientist
