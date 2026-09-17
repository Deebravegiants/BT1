# [H] OpenKM XXE Injection

## Summary
Severity: High
Advisory: CVE-2022-2131
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L)
Published: 2022-07-25
Source: https://osv.dev/vulnerability/CVE-2022-2131
Type: osv

## Details
OpenKM Community Edition in its 6.3.10 version and before was using XMLReader parser in XMLTextExtractor.java file without the required security flags, allowing an attacker to perform a XML external entity injection attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2131.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2131
- https://www.incibe-cert.es/en/early-warning/security-advisories/openkm-xxe-injection
