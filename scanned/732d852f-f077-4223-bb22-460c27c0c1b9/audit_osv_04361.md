# [C] Discourse vulnerable to RCE via admins uploading maliciously zipped file

## Summary
Severity: Critical
Advisory: BIT-discourse-2022-36066
Aliases: CVE-2022-36066, GHSA-grvh-qcpg-hfmv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-36066
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.9

## Details
Discourse is an open source discussion platform. In versions prior to 2.8.9 on the `stable` branch and prior to 2.9.0.beta10 on the `beta` and `tests-passed` branches, admins can upload a maliciously crafted Zip or Gzip Tar archive to write files at arbitrary locations and trigger remote code execution. The problem is patched in version 2.8.9 on the `stable` branch and version 2.9.0.beta10 on the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/b27d5626d208a22c516a0adfda7554b67b493835
- https://github.com/discourse/discourse/pull/18421
- https://github.com/discourse/discourse/security/advisories/GHSA-grvh-qcpg-hfmv
- https://nvd.nist.gov/vuln/detail/CVE-2022-36066
