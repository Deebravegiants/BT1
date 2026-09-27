# [C] Discourse vulnerable to auto-executing of third-party code in embedded CodePen iframe

## Summary
Severity: Critical
Advisory: BIT-discourse-2025-48877
Aliases: CVE-2025-48877, GHSA-cm93-6m2m-cjcv
Ecosystem: Bitnami
Published: 2025-06-11
Source: https://osv.dev/vulnerability/BIT-discourse-2025-48877
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.4

## Details
Discourse is an open-source discussion platform. Prior to version 3.4.4 of the `stable` branch, version 3.5.0.beta5 of the `beta` branch, and version 3.5.0.beta6-dev of the `tests-passed` branch, Codepen is present in the default `allowed_iframes` site setting, and it can potentially auto-run arbitrary JS in the iframe scope, which is unintended. This issue is patched in version 3.4.4 of the `stable` branch, version 3.5.0.beta5 of the `beta` branch, and version 3.5.0.beta6-dev of the `tests-passed` branch. As a workaround, the Codepen prefix can be removed from a site's `allowed_iframes`.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-cm93-6m2m-cjcv
- https://nvd.nist.gov/vuln/detail/CVE-2025-48877
