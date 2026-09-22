# [C] Misskey's Incomplete Patch of CVE-2024-52591 Leads to Forgery of Federated Notes

## Summary
Severity: Critical
Advisory: CVE-2025-25306
Aliases: GHSA-6w2c-vf6f-xf26
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/CVE-2025-25306
Type: osv

## Details
Misskey is an open source, federated social media platform. The patch for CVE-2024-52591 did not sufficiently validate the relation between the `id` and `url` fields of ActivityPub objects. An attacker can forge an object where they claim authority in the `url` field even if the specific ActivityPub object type require authority in the `id` field. Version 2025.2.1 addresses the issue.

## References
- https://github.com/misskey-dev/misskey/releases/tag/2025.2.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25306.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-6w2c-vf6f-xf26
- https://nvd.nist.gov/vuln/detail/CVE-2025-25306
