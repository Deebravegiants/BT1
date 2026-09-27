# [M] Tendenci is Vulnerable to CSV Formula Injection through its Contact Form Message Field 

## Summary
Severity: Medium
Advisory: GHSA-4q3w-jgfx-4792
CVE: CVE-2020-36962
CWE: CWE-1236
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-4q3w-jgfx-4792
Type: github-advisory

## Affected
- PyPI: `tendenci` — affected >=0 <12.3.2

## Details
Tendenci 12.3.1 contains a CSV formula injection vulnerability in the contact form message field that allows attackers to inject malicious formulas during export. Attackers can submit crafted payloads like '=10+20+cmd|' /C calc'!A0' in the message field to trigger arbitrary command execution when the CSV is opened in spreadsheet applications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36962
- https://github.com/tendenci/tendenci/commit/3e37622cac81440c5a1f97c39f112a2cf4a5450c
- https://github.com/pypa/advisory-database/tree/main/vulns/tendenci/PYSEC-2026-136.yaml
- https://github.com/tendenci/tendenci
- https://www.exploit-db.com/exploits/49145
- https://www.tendenci.com
- https://www.vulncheck.com/advisories/tendenci-csv-formula-injection
