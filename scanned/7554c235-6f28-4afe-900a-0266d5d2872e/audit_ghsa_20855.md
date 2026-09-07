# [C] com.google.cloud.tools:jib-core vulnerable to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: GHSA-936v-cg49-m2g5
CVE: CVE-2022-25914
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-09
Source: https://github.com/advisories/GHSA-936v-cg49-m2g5
Type: github-advisory

## Affected
- Maven: `com.google.cloud.tools:jib-core` — affected >=0 <0.22.0

## Details
The package com.google.cloud.tools:jib-core before 0.22.0 are vulnerable to Remote Code Execution (RCE) via the isDockerInstalled function, due to attempting to execute input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25914
- https://github.com/GoogleContainerTools/jib/pull/3744
- https://github.com/GoogleContainerTools/jib/commit/67fa40bc2c484da0546333914ea07a89fe44eaaf
- https://github.com/GoogleContainerTools/jib
- https://security.snyk.io/vuln/SNYK-JAVA-COMGOOGLECLOUDTOOLS-2968871
