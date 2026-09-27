# [C] External Entity Reference in TwelveMonkeys ImageIO

## Summary
Severity: Critical
Advisory: GHSA-pjch-4g28-fxx7
CVE: CVE-2021-23792
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-07
Source: https://github.com/advisories/GHSA-pjch-4g28-fxx7
Type: github-advisory

## Affected
- Maven: `com.twelvemonkeys.imageio:imageio-metadata` — affected >=0 <3.7.1

## Details
The package com.twelvemonkeys.imageio:imageio-metadata before version 3.7.1 is vulnerable to XML External Entity (XXE) Injection due to an insecurely initialized XML parser for reading XMP Metadata. An attacker can exploit this vulnerability if they are able to supply a file (e.g. when an online profile picture is processed) with a malicious XMP segment. If the XMP metadata of the uploaded image is parsed, then the XXE vulnerability is triggered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23792
- https://github.com/haraldk/TwelveMonkeys/commit/da4efe98bf09e1cce91b7633cb251958a200fc80
- https://github.com/haraldk/TwelveMonkeys
- https://snyk.io/vuln/SNYK-JAVA-COMTWELVEMONKEYSIMAGEIO-2316763
