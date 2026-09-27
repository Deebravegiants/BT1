# [H] Coolify: OS Command Injection via Unmanaged Container Operations - Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-34058
Aliases: GHSA-rh5x-qx77-fq9v
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34058
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the Livewire component Server\Resources exposes public methods (startUnmanaged, stopUnmanaged, restartUnmanaged) that accept a container ID parameter directly from the browser without any sanitization or escaping. This parameter is interpolated directly into shell commands executed via SSH on managed servers, enabling any authenticated team member to execute arbitrary OS commands on remote servers. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34058.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-rh5x-qx77-fq9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34058
- https://github.com/coollabsio/coolify/commit/944a038349216f00b390e905c121355adc8b23c1
- https://github.com/coollabsio/coolify/pull/9172
