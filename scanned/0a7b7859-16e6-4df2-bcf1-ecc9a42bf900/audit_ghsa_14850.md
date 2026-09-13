# [C] parisneo/lollms Local File Inclusion (LFI) attack

## Summary
Severity: Critical
Advisory: GHSA-vqwr-q6cc-c242
CVE: CVE-2024-4315
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-06-12
Source: https://github.com/advisories/GHSA-vqwr-q6cc-c242
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <9.5.0

## Details
parisneo/lollms version 9.5 is vulnerable to Local File Inclusion (LFI) attacks due to insufficient path sanitization. The `sanitize_path_from_endpoint` function fails to properly sanitize Windows-style paths (backward slash `\`), allowing attackers to perform directory traversal attacks on Windows systems. This vulnerability can be exploited through various routes, including `personalities` and `/del_preset`, to read or delete any file on the Windows filesystem, compromising the system's availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4315
- https://github.com/parisneo/lollms/commit/95ad36eeffc6a6be3e3f35ed35a384d768f0ecf6
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/8a1b0197-2c36-4276-b92b-630a2a9bb09c
