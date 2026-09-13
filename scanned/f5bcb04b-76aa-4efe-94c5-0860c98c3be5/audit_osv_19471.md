# [H] CVE-2021-21372

## Summary
Severity: High
Advisory: CVE-2021-21372
Aliases: GHSA-rg9f-w24h-962p
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-21372
Type: osv

## Details
Nimble is a package manager for the Nim programming language. In Nim release version before versions 1.2.10 and 1.4.4, Nimble doCmd is used in different places and can be leveraged to execute arbitrary commands. An attacker can craft a malicious entry in the packages.json package list to trigger code execution.

## References
- https://github.com/nim-lang/nimble/blob/master/changelog.markdown#0130
- https://github.com/nim-lang/security/security/advisories/GHSA-rg9f-w24h-962p
- https://github.com/nim-lang/nimble/commit/7bd63d504a4157b8ed61a51af47fb086ee818c37
- https://consensys.net/diligence/vulnerabilities/nim-insecure-ssl-tls-defaults-remote-code-execution/
