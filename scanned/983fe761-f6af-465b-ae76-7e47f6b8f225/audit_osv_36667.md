# [H] openITCOCKPIT has Unsafe Deserialization in openITCOCKPIT Changelog Handling

## Summary
Severity: High
Advisory: CVE-2026-24892
Aliases: GHSA-g83p-vvjm-g39x
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-24892
Type: osv

## Details
openITCOCKPIT is an open source monitoring tool built for different monitoring engines like Nagios, Naemon and Prometheus. openITCOCKPIT Community Edition 5.3.1 and earlier contains an unsafe PHP deserialization pattern in the processing of changelog entries. Serialized changelog data derived from attacker-influenced application state is unserialized without restricting allowed classes. Although no current application endpoint was found to introduce PHP objects into this data path, the presence of an unrestricted unserialize() call constitutes a latent PHP object injection vulnerability. If future code changes, plugins, or refactors introduce object values into this path, the vulnerability could become immediately exploitable with severe impact, including potential remote code execution.

## References
- https://github.com/openITCOCKPIT/openITCOCKPIT/releases/tag/openITCOCKPIT-5.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24892.json
- https://github.com/openITCOCKPIT/openITCOCKPIT/security/advisories/GHSA-g83p-vvjm-g39x
- https://nvd.nist.gov/vuln/detail/CVE-2026-24892
- https://github.com/openITCOCKPIT/openITCOCKPIT/commit/975e0d0dfb79898568afbbfdba8f647d92612a69
