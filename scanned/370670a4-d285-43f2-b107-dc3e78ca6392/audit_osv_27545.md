# [M] discourse-ai admin-initiated SSRF when interacting with AI services

## Summary
Severity: Medium
Advisory: CVE-2024-23654
Aliases: GHSA-32cj-rm2q-22cc
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-23654
Type: osv

## Details
discourse-ai is the AI plugin for the open-source discussion platform Discourse. Prior to commit 94ba0dadc2cf38e8f81c3936974c167219878edd, interactions with different AI services are vulnerable to admin-initiated SSRF attacks. Versions of the plugin that include commit 94ba0dadc2cf38e8f81c3936974c167219878edd contain a patch. As a workaround, one may disable the discourse-ai plugin.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23654.json
- https://github.com/discourse/discourse-ai/security/advisories/GHSA-32cj-rm2q-22cc
- https://nvd.nist.gov/vuln/detail/CVE-2024-23654
- https://github.com/discourse/discourse-ai/commit/94ba0dadc2cf38e8f81c3936974c167219878edd
