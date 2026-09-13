# [M] miniserve affected by a TOCTOU and symlink race vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mxc8-4jqf-368q
CVE: CVE-2025-67124
CWE: CWE-367, CWE-59
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-mxc8-4jqf-368q
Type: github-advisory

## Affected
- crates.io: `miniserve` — affected >=0 <0.32.0

## Details
A TOCTOU and symlink race in svenstaro/miniserve 0.32.0 upload finalization (when uploads are enabled) can allow an attacker to overwrite arbitrary files outside the intended upload/document root in deployments where the attacker can create/replace filesystem entries in the upload destination directory (e.g., shared writable directory/volume).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67124
- https://gist.github.com/thesmartshadow/55688f87f8b985eb530e07d00ef8c63f
- https://github.com/svenstaro/miniserve
