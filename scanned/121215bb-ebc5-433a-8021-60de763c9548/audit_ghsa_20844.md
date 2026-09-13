# [H] Goomph before 3.37.2 allows malicious zip file to write contents to arbitrary locations

## Summary
Severity: High
Advisory: GHSA-p2f7-9cv7-jjf6
CVE: CVE-2022-26049
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-12
Source: https://github.com/advisories/GHSA-p2f7-9cv7-jjf6
Type: github-advisory

## Affected
- Maven: `com.diffplug.gradle:goomph` — affected >=0 <3.37.2

## Details
This affects the package com.diffplug.gradle:goomph before 3.37.2. It allows a malicious zip file to potentially break out of the expected destination directory, writing contents into arbitrary locations on the file system. Overwriting certain files/directories could allow an attacker to achieve remote code execution on a target system by exploiting this vulnerability.

**Note:** This could have allowed a malicious zip file to extract itself into an arbitrary directory. The only file that Goomph extracts is the p2 bootstrapper and eclipse metadata files hosted at eclipse.org, which are not malicious, so the only way this vulnerability could have affected you is if you had set a custom bootstrap zip, and that zip was malicious.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26049
- https://github.com/diffplug/goomph/pull/198
- https://github.com/diffplug/goomph/commit/25f04f67ba62d9a14104bee13a0a0f2517afb8c8
- https://security.snyk.io/vuln/SNYK-JAVA-COMDIFFPLUGGRADLE-2981040
