# [M] ParquetSharp: Possible Stack Overflow When Reading a ParquetFile with Large Decimal Type Width

## Summary
Severity: Medium
Advisory: GHSA-rrjr-v56m-ww88
CVE: CVE-2026-42241
CWE: CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-rrjr-v56m-ww88
Type: github-advisory

## Affected
- NuGet: `ParquetSharp` — affected >=18.1.0 <23.0.0.1

## Details
`DecimalConverter.ReadDecimal` makes a stackalloc using what might be an attacker-supplied value. If an attacker declares a decimal column with some unreasonable width, this could lead to a stack overflow. In a service environment, this would potentially take down a service.

This affects applications using ParquetSharp to read untrusted Parquet files in a network service.

## References
- https://github.com/G-Research/ParquetSharp/security/advisories/GHSA-rrjr-v56m-ww88
- https://nvd.nist.gov/vuln/detail/CVE-2026-42241
- https://github.com/G-Research/ParquetSharp
- https://github.com/G-Research/ParquetSharp/releases/tag/23.0.0.1
