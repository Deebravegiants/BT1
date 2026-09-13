# [H] Discourse DoS through Onebox favicon URL

## Summary
Severity: High
Advisory: BIT-discourse-2023-47120
Aliases: CVE-2023-47120, GHSA-77cw-xhj8-hfp3
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-47120
Type: osv

## Affected
- Bitnami: `discourse` — affected >=3.1.0 <3.1.3

## Details
Discourse is an open source platform for community discussion. In versions 3.1.0 through 3.1.2 of the `stable` branch and versions 3.1.0,beta6 through 3.2.0.beta2 of the `beta` and `tests-passed` branches, Redis memory can be depleted by crafting a site with an abnormally long favicon URL and drafting multiple posts which Onebox it. The issue is patched in version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/95a82d608d6377faf68a0e2c5d9640b043557852
- https://github.com/discourse/discourse/commit/e910dd09140cb4abc3a563b95af4a137ca7fa0ce
- https://github.com/discourse/discourse/security/advisories/GHSA-77cw-xhj8-hfp3
- https://nvd.nist.gov/vuln/detail/CVE-2023-47120
