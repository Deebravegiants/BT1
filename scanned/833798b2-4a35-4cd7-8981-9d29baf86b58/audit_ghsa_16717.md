# [M] Pterodactyl Wings vulnerable to Server-Side Request Forgery during remote file pull

## Summary
Severity: Medium
Advisory: GHSA-qq22-jj8x-4wwv
CVE: CVE-2024-34068
CWE: CWE-284, CWE-441, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-qq22-jj8x-4wwv
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.11.12

## Details
### Impact

An authenticated user who has access to a game server is able to bypass the previously implemented access control (https://github.com/pterodactyl/wings/security/advisories/GHSA-6rg3-8h8x-5xfv) that prevents accessing internal endpoints of the node hosting Wings in the pull endpoint. This would allow malicious users to potentially access resources on local networks that would otherwise be inaccessible.

### Workarounds

Enabling the `api.disable_remote_download` option or updating to the latest version of Wings are the only known workarounds.

### Patches

https://github.com/pterodactyl/wings/commit/c152e36101aba45d8868a9a0eeb890995e8934b8

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-6rg3-8h8x-5xfv
- https://github.com/pterodactyl/wings/security/advisories/GHSA-qq22-jj8x-4wwv
- https://nvd.nist.gov/vuln/detail/CVE-2024-34068
- https://github.com/pterodactyl/wings/commit/c152e36101aba45d8868a9a0eeb890995e8934b8
- https://github.com/pterodactyl/wings
- https://pkg.go.dev/vuln/GO-2024-2815
