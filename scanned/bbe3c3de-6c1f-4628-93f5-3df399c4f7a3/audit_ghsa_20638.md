# [H] Uncontrolled Resource Consumption in snakeyaml

## Summary
Severity: High
Advisory: GHSA-3mc7-4q67-w48m
CVE: CVE-2022-25857
CWE: CWE-400, CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-31
Source: https://github.com/advisories/GHSA-3mc7-4q67-w48m
Type: github-advisory

## Affected
- Maven: `org.yaml:snakeyaml` — affected >=0 <1.31

## Details
The package org.yaml:snakeyaml from 0 and before 1.31 are vulnerable to Denial of Service (DoS) due missing to nested depth limitation for collections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25857
- https://github.com/snakeyaml/snakeyaml/commit/fc300780da21f4bb92c148bc90257201220cf174
- https://bitbucket.org/snakeyaml/snakeyaml/commits/fc300780da21f4bb92c148bc90257201220cf174
- https://bitbucket.org/snakeyaml/snakeyaml/issues/525
- https://github.com/snakeyaml/snakeyaml
- https://lists.debian.org/debian-lts-announce/2022/10/msg00001.html
- https://security.netapp.com/advisory/ntap-20240315-0010
- https://security.snyk.io/vuln/SNYK-JAVA-ORGYAML-2806360
