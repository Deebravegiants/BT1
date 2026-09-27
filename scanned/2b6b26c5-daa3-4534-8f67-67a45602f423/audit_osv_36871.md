# [H] Penpot has Arbitrary File Read via create-font-variant RPC endpoint

## Summary
Severity: High
Advisory: CVE-2026-26202
Aliases: GHSA-xp3f-g8rq-9px2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-26202
Type: osv

## Details
Penpot is an open-source design tool for design and code collaboration. Prior to version 2.13.2, an authenticated user can read arbitrary files from the server by supplying a local file path (e.g. `/etc/passwd`) as a font data chunk in the `create-font-variant` RPC endpoint, resulting in the file contents being stored and retrievable as a "font" asset. This is an arbitrary file read vulnerability. Any authenticated user with team edit permissions can read arbitrary files accessible to the Penpot backend process on the host filesystem. This can lead to exposure of sensitive system files, application secrets, database credentials, and private keys, potentially enabling further compromise of the server. In containerized deployments, the blast radius may be limited to the container filesystem, but environment variables, mounted secrets, and application configuration are still at risk. Version 2.13.2 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26202.json
- https://github.com/penpot/penpot/security/advisories/GHSA-xp3f-g8rq-9px2
- https://nvd.nist.gov/vuln/detail/CVE-2026-26202
- https://github.com/penpot/penpot/commit/06e5825c8a0209889966a4eb5152efd6ff108626
