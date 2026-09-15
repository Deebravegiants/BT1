# [H] Nix Hydra Missing authentication when triggering evaluations

## Summary
Severity: High
Advisory: CVE-2024-45049
Aliases: GHSA-xv29-v93r-2f5v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-27
Source: https://osv.dev/vulnerability/CVE-2024-45049
Type: osv

## Details
Hydra is a Continuous Integration service for Nix based projects. It is possible to trigger evaluations in Hydra without any authentication. Depending on the size of evaluations, this can impact the availability of systems. The problem can be fixed by applying https://github.com/NixOS/hydra/commit/f73043378907c2c7e44f633ad764c8bdd1c947d5 to any Hydra package. Users are advised to upgrade. Users unable to upgrade should deny the `/api/push` route in a reverse proxy. This also breaks the "Evaluate jobset" button in the frontend.

## References
- https://mastodon.delroth.net/@delroth/113029832631860419
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45049.json
- https://github.com/NixOS/hydra/security/advisories/GHSA-xv29-v93r-2f5v
- https://nvd.nist.gov/vuln/detail/CVE-2024-45049
- https://github.com/NixOS/hydra/commit/f73043378907c2c7e44f633ad764c8bdd1c947d5
- https://github.com/NixOS/nixpkgs/pull/337766
