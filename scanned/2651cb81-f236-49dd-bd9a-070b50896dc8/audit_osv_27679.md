# [H] Crafatar path traversal vulnerability

## Summary
Severity: High
Advisory: CVE-2024-24756
Aliases: GHSA-5cxq-25mp-q5f2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-01
Source: https://osv.dev/vulnerability/CVE-2024-24756
Type: osv

## Details
Crafatar serves Minecraft avatars based on the skin for use in external applications. Files outside of the `lib/public/` directory can be requested from the server. Instances running behind Cloudflare (including crafatar.com) are not affected. Instances using the Docker container as shown in the README are affected, but only files within the container can be read. By default, all of the files within the container can also be found in this repository and are not confidential. This vulnerability is patched in 2.1.5.

## References
- https://github.com/crafatar/crafatar/blob/e0233f2899a3206a817d2dd3b80da83d51c7a726/lib/server.js#L64-L67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24756.json
- https://github.com/crafatar/crafatar/security/advisories/GHSA-5cxq-25mp-q5f2
- https://nvd.nist.gov/vuln/detail/CVE-2024-24756
- https://github.com/crafatar/crafatar/commit/bba004acc725b362a5d2d5dfe30cf60e7365a373
