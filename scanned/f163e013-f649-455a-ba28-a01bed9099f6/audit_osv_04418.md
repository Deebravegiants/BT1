# [M] Bypassing height value allowed in some theme components

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-46130
Aliases: CVE-2023-46130, GHSA-c876-638r-vfcg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-46130
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.0

## Details
Discourse is an open source platform for community discussion. Prior to version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches, some theme components allow users to add svgs with unlimited `height` attributes, and this can affect the availability of subsequent replies in a topic. Most Discourse instances are unaffected, only instances with the svgbob or the mermaid theme component are within scope. The issue is patched in version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches. As a workaround, disable or remove the relevant theme components.

## References
- https://github.com/discourse/discourse/commit/6183d9633de873ac2b1e9cdb6ac1c94b4ffae9cb
- https://github.com/discourse/discourse/commit/89a2e60706ce22e4afc463d03af2f34c53291800
- https://github.com/discourse/discourse/security/advisories/GHSA-c876-638r-vfcg
- https://nvd.nist.gov/vuln/detail/CVE-2023-46130
