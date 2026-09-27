# [H] CVE-2021-21420

## Summary
Severity: High
Advisory: CVE-2021-21420
Aliases: GHSA-j6x4-4622-8vv3
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-01
Source: https://osv.dev/vulnerability/CVE-2021-21420
Type: osv

## Details
vscode-stripe is an extension for Visual Studio Code. A vulnerability in Stripe for Visual Studio Code extension exists when it loads an untrusted source-code repository containing malicious settings. An attacker who successfully exploited the vulnerability could run arbitrary code in the context of the current user. The update addresses the vulnerability by modifying the way the extension validates its settings.

## References
- https://github.com/stripe/vscode-stripe/security/advisories/GHSA-j6x4-4622-8vv3
