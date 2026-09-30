# [C] BIT-ghost-2022-27139

## Summary
Severity: Critical
Advisory: BIT-ghost-2022-27139
Aliases: CVE-2022-27139, GHSA-fvc6-qjp7-m4g4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ghost-2022-27139
Type: osv

## Affected
- Bitnami: `ghost` — affected >=4.39.0 <4.39.1

## Details
An arbitrary file upload vulnerability in the file upload module of Ghost v4.39.0 allows attackers to execute arbitrary code via a crafted SVG file. NOTE: Vendor states that as outlined in Ghost's security documentation, upload of SVGs is only possible by trusted authenticated users. The uploading of SVG files to Ghost does not represent a remote code execution vulnerability. SVGs are not executable on the server, and may only execute javascript in a client's browser - this is expected and intentional functionality

## References
- http://ghost.org/docs/security/#privilege-escalation-attacks
- https://youtu.be/FCqWEvir2wE
- https://nvd.nist.gov/vuln/detail/CVE-2022-27139
