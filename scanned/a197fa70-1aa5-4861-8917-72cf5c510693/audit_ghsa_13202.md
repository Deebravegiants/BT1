# [H] hson-java vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-94w5-rf69-2h6c
CVE: CVE-2023-39685
CWE: CWE-125, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-01
Source: https://github.com/advisories/GHSA-94w5-rf69-2h6c
Type: github-advisory

## Affected
- Maven: `org.hjson:hjson` — affected >=0 <3.0.1

## Details
An issue in hjson-java up to v3.0.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted JSON string to string a `StringIndexOutOfBoundsException`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39685
- https://github.com/hjson/hjson-java/issues/27
- https://github.com/hjson/hjson-java/commit/aff0b607929b4397d93dc0d029a56aeefb242602
- https://github.com/hjson/hjson-java
