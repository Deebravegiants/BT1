# [C] CVE-2020-7622

## Summary
Severity: Critical
Advisory: CVE-2020-7622
Aliases: GHSA-gv3v-92v6-m48j
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-06
Source: https://osv.dev/vulnerability/CVE-2020-7622
Type: osv

## Details
This affects the package io.jooby:jooby-netty before 1.6.9, from 2.0.0 and before 2.2.1. The DefaultHttpHeaders is set to false which means it does not validates that the header isn't being abused for HTTP Response Splitting.

## References
- https://github.com/jooby-project/jooby/commit/b66e3342cf95205324023cfdf2cb5811e8a6dcf4
- https://snyk.io/vuln/SNYK-JAVA-IOJOOBY-564249
- https://github.com/jooby-project/jooby/security/advisories/GHSA-gv3v-92v6-m48j
