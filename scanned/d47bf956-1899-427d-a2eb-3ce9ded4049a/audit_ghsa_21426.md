# [H] HTSJDK is vulnerable to exposure of resource(s) to the wrong sphere

## Summary
Severity: High
Advisory: GHSA-96vh-4rfp-c42c
CVE: CVE-2022-21126
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-29
Source: https://github.com/advisories/GHSA-96vh-4rfp-c42c
Type: github-advisory

## Affected
- Maven: `com.github.samtools:htsjdk` — affected >=0 <3.0.1

## Details
The package com.github.samtools:htsjdk before 3.0.1 are vulnerable to Creation of Temporary File in Directory with Insecure Permissions due to the createTempDir() function in util/IOUtil.java not checking for the existence of the temporary directory before attempting to create it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21126
- https://github.com/samtools/htsjdk/pull/1617
- https://github.com/samtools/htsjdk/commit/4a4024a97ee3e87096df6ad9b22c8260bd527772
- https://github.com/samtools/htsjdk
- https://security.snyk.io/vuln/SNYK-JAVA-COMGITHUBSAMTOOLS-3149901
