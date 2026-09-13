# [H] Langroid Allows XXE Injection via XMLToolMessage

## Summary
Severity: High
Advisory: GHSA-pw95-88fg-3j6f
CVE: CVE-2025-46726
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-pw95-88fg-3j6f
Type: github-advisory

## Affected
- PyPI: `langroid` — affected >=0 <0.53.4

## Details
### Summary
A LLM application leveraging `XMLToolMessage` class may be exposed to untrusted XML input that could result in DoS and/or exposing local files with sensitive information.

### Details
`XMLToolMessage` uses `lxml` without safeguards:
https://github.com/langroid/langroid/blob/df6227e6c079ec22bb2768498423148d6685acff/langroid/agent/xml_tool_message.py#L51-L52
`lxml` is vulnerable to quadratic blowup attacks and processes external entity declarations for local files by default. 
Check here: https://pypi.org/project/defusedxml/#python-xml-libraries

### PoC
A typical Quadratic blowup XML payload looks like this:
```xml
<!DOCTYPE bomb [
<!ENTITY a "aaaaaaaaaa">
<!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
<!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">
]>
<bomb>&c;</bomb>
```
Here, &a; expands to 10 characters, &b; expands to 100, and &c; expands to 1000, causing exponential memory usage and potentially crashing the application.
 
### Fix
Langroid 0.53.4 initializes `XMLParser` with flags to prevent XML External Entity (XXE), billion laughs, and external DTD attacks by disabling entity resolution, DTD loading, and network access.
https://github.com/langroid/langroid/commit/36e7e7db4dd1636de225c2c66c84052b1e9ac3c3

## References
- https://github.com/langroid/langroid/security/advisories/GHSA-pw95-88fg-3j6f
- https://nvd.nist.gov/vuln/detail/CVE-2025-46726
- https://github.com/langroid/langroid/commit/36e7e7db4dd1636de225c2c66c84052b1e9ac3c3
- https://github.com/langroid/langroid
- https://github.com/langroid/langroid/blob/df6227e6c079ec22bb2768498423148d6685acff/langroid/agent/xml_tool_message.py#L51-L52
