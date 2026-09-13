# [M] RapidRAW < 1.6.0 NTLMv2 Credential Leak via UNC Path in lutPath

## Summary
Severity: Medium
Advisory: CVE-2026-64816
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-64816
Type: osv

## Details
RapidRAW before 1.6.0 does not validate the lutPath field in preset files before passing it to File::open() in lut_processing.rs. On Windows, a UNC path in lutPath causes an outbound SMB connection to an attacker-controlled host, leaking the victim's NTLMv2 credentials. The vulnerable code path is reachable through two vectors: community presets fetched automatically from the remote preset repository when the victim opens the Community tab, and individual preset files imported directly by the victim via the preset import feature (handle_import_presets_from_file in file_management.rs). The second vector does not require control of the community preset repository and is triggered when a user imports a preset file shared through Discord, forums, or similar channels.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64816.json
- https://github.com/CyberTimon/RapidRAW/releases/tag/v1.6.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-64816
- https://www.vulncheck.com/advisories/rapidraw-ntlmv2-credential-leak-via-unc-path-in-lutpath
- https://github.com/CyberTimon/RapidRAW/commit/83852f36ba4a260be
- https://github.com/CyberTimon/RapidRAW
