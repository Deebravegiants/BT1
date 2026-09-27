# [C] Jellyfin Possible Organization/Secret Compromise from dangerous CI implementation

## Summary
Severity: Critical
Advisory: CVE-2026-31852
Aliases: GHSA-7qhm-2m45-7fmh
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31852
Type: osv

## Details
Jellyfin is an open-source media system. The code-quality.yml GitHub Actions workflow in jellyfin/jellyfin-ios is vulnerable to arbitrary code execution via pull requests from forked repositories. Due to the workflow's elevated permissions (nearly all write permissions), this vulnerability enables full repository takeover of jellyfin/jellyfin-ios, exfiltration of highly privileged secrets, Apple App Store supply chain attack, GitHub Container Registry (ghcr.io) package poisoning, and full jellyfin organization compromise via cross-repository token usage. Note: This is not a code vulnerability, but a vulnerability in the GitHub Actions workflows. No new version is required for this GHSA and end users do not need to take any actions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31852.json
- https://github.com/jellyfin/jellyfin-ios/security/advisories/GHSA-7qhm-2m45-7fmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-31852
- https://github.com/jellyfin/jellyfin-ios/commit/109217e75f38394b2f6e46e25dfe5a721203d3c8
