# [M] Resource Exhaustion in Carbone

## Summary
Severity: Medium
Advisory: CVE-2026-18929
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-18929
Type: osv

## Details
Carbone is vulnerable to Denial of Service due to lack of protection against zip bombs when processing .docx files. The library uses yazl for zip decompression without validating entry sizes, allowing an attacker to supply a malicious .docx file containing a zip bomb that decompresses to a significantly larger size, causing excessive memory consumption and crashing the application server.




The issue was fixed in versions: 3.8.2, 4.26.3 and 5.4.4.  The fix is available across all distribution types.

## References
- https://carbone.io/
- https://cert.pl/en/posts/2026/08/CVE-2026-18929
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18929.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18929
- https://github.com/carboneio/carbone/commit/eb9b4cff992cc1cb1a319d7fc0cbd09160dc214e
- https://github.com/carboneio/carbone
