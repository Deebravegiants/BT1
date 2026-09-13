# [H] Coolify: Authenticated Host RCE

## Summary
Severity: High
Advisory: CVE-2026-34597
Aliases: GHSA-9pp4-wcmj-rq73
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-34597
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.470, a critical Authenticated Host Remote Code Execution (RCE) vulnerability was discovered in Coolify. The flaw resides in the handling of user-defined build parameters for the Nixpacks build pack. Specifically, the install_command provided by a user is directly concatenated into a shell command string that is executed on the deployment host during the building phase. An attacker can leverage this to escape the intended build context and execute arbitrary commands with host-level privileges. This vulnerability is fixed in 4.0.0-beta.470.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34597.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-9pp4-wcmj-rq73
- https://nvd.nist.gov/vuln/detail/CVE-2026-34597
