# [H] Discourse vulnerable to ReDoS in user agent parsing

## Summary
Severity: High
Advisory: BIT-discourse-2023-23621
Aliases: CVE-2023-23621, GHSA-mrfp-54hf-jrcv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23621
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.0.1 on the `stable` branch and version 3.1.0.beta2 on the `beta` and `tests-passed` branches, a malicious user can cause a regular expression denial of service using a carefully crafted user agent. This issue is patched in version 3.0.1 on the `stable` branch and version 3.1.0.beta2 on the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/6d92c3cbdac431db99a450f360a3048bb3aaf458
- https://github.com/discourse/discourse/pull/20002
- https://github.com/discourse/discourse/security/advisories/GHSA-mrfp-54hf-jrcv
- https://nvd.nist.gov/vuln/detail/CVE-2023-23621
