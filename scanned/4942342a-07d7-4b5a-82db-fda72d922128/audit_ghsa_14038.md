# [C] glazedlists XML Deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-p6m6-9j36-vfjx
CVE: CVE-2023-31890
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-p6m6-9j36-vfjx
Type: github-advisory

## Affected
- Maven: `com.glazedlists:glazedlists` — affected 1.11.0

## Details
An XML Deserialization vulnerability in glazedlists v1.11.0 allows an attacker to execute arbitrary code via the BeanXMLByteCoder.decode() parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31890
- https://github.com/glazedlists/glazedlists/issues/709
- https://github.com/glazedlists/glazedlists
- https://github.com/glazedlists/glazedlists/blob/e0593e338246945dab4e83356ef44a59db172a80/extensions/io/src/main/java/ca/odell/glazedlists/impl/io/BeanXMLByteCoder.java
