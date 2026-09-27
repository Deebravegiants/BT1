# [C] Linkr allows manifest tampering leading to arbitrary file injection

## Summary
Severity: Critical
Advisory: CVE-2025-59334
Aliases: GHSA-6wph-mpv2-29xv
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-59334
Type: osv

## Details
Linkr is a lightweight file delivery system that downloads files from a webserver. Linkr versions through 2.0.0 do not verify the integrity or authenticity of .linkr manifest files before using their contents, allowing a tampered manifest to inject arbitrary file entries into a package distribution. An attacker can modify a generated .linkr manifest (for example by adding a new entry with a malicious URL) and when a user runs the extract command the client downloads the attacker-supplied file without verification. This enables arbitrary file injection and creates a potential path to remote code execution if a downloaded malicious binary or script is later executed. Version 2.0.1 adds a manifest integrity check that compares the checksum of the original author-created manifest to the one being extracted and aborts on mismatch, warning if no original manifest is hosted. Users should update to 2.0.1 or later. As a workaround prior to updating, use only trusted .linkr manifests, manually verify manifest integrity, and host manifests on trusted servers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59334.json
- https://github.com/mohammadzain2008/Linkr/security/advisories/GHSA-6wph-mpv2-29xv
- https://nvd.nist.gov/vuln/detail/CVE-2025-59334
- https://github.com/mohammadzain2008/Linkr/commit/182e5ddaa51972e144005b500c4bcebf2fd1a6c0
