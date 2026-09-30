# [M] User's bio visible even if profile is restricted in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-21678
Aliases: CVE-2022-21678, GHSA-jwww-46gv-564m
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-21678
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.13

## Details
Discourse is an open source discussion platform. Prior to version 2.8.0.beta11 in the `tests-passed` branch, version 2.8.0.beta11 in the `beta` branch, and version 2.7.13 in the `stable` branch, the bios of users who made their profiles private were still visible in the `<meta>` tags on their users' pages. The problem is patched in `tests-passed` version 2.8.0.beta11, `beta` version 2.8.0.beta11, and `stable` version 2.7.13 of Discourse.

## References
- https://github.com/discourse/discourse/commit/5e2e178fcfb490c37b9f8bb9f737185441b1d6de
- https://github.com/discourse/discourse/commit/c0bb775f3f35b1b0d04a5b2a984f57c3e39f9e6c
- https://github.com/discourse/discourse/security/advisories/GHSA-jwww-46gv-564m
- https://nvd.nist.gov/vuln/detail/CVE-2022-21678
