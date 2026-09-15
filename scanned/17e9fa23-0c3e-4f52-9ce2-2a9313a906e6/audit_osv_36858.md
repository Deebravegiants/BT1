# [C] emp3r0r Agent-Controlled Metadata to Operator RCE (tmux Command Injection)

## Summary
Severity: Critical
Advisory: CVE-2026-26068
Aliases: GHSA-h5p4-4xp4-vjpp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-26068
Type: osv

## Details
emp3r0r is a stealth-focused C2 designed by Linux users for Linux environments. Prior to 3.21.1, untrusted agent metadata (Transport, Hostname) is accepted during check-in and later interpolated into tmux shell command strings executed via /bin/sh -c. This enables command injection and remote code execution on the operator host. This vulnerability is fixed in 3.21.1.

## References
- https://github.com/jm33-m0/emp3r0r/releases/tag/v3.21.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26068.json
- https://github.com/jm33-m0/emp3r0r/security/advisories/GHSA-h5p4-4xp4-vjpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-26068
- https://github.com/jm33-m0/emp3r0r/commit/0cd64e4a26e7839a9a54bca3d756a665fcb7fda0
