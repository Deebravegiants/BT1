# [H] Coolify: Authenticated Remote Code Execution via Command Injection in Database Import Container Name

## Summary
Severity: High
Advisory: CVE-2026-34057
Aliases: GHSA-6r3g-w7x8-54fj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34057
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the database import Livewire component (app/Livewire/Project/Database/Import.php) allows client-controlled container and server properties to reach shell commands without locking or validation, allowing an authenticated user to inject commands through a database import container name. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34057.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-6r3g-w7x8-54fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34057
- https://github.com/coollabsio/coolify/commit/d486bf09ab2da8ad78fa721a079f066c76ce08d2
