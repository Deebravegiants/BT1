# [M] moby Access to remapped root allows privilege escalation to real root

## Summary
Severity: Medium
Advisory: GHSA-7452-xqpj-6rpc
CVE: CVE-2021-21284
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-7452-xqpj-6rpc
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <19.3.15
- Go: `github.com/moby/moby` — affected >=20.10.0-beta1 <20.10.3

## Details
### Impact

When using `--userns-remap`, if the root user in the remapped namespace has access to the host filesystem they can modify files under `/var/lib/docker/<remapping>` that cause writing files with extended privileges.

### Patches

Versions 20.10.3 and 19.03.15 contain patches that prevent privilege escalation from remapped user.

### Credits

Maintainers would like to thank Alex Chapman for discovering the vulnerability; @awprice, @nathanburrell, @raulgomis, @chris-walz, @erin-jensby, @bassmatt, @mark-adams, @dbaxa for working on it and Zac Ellis for responsibly disclosing it to security@docker.com

## References
- https://github.com/moby/moby/security/advisories/GHSA-7452-xqpj-6rpc
- https://nvd.nist.gov/vuln/detail/CVE-2021-21284
- https://github.com/moby/moby/commit/64bd4485b3a66a597c02c95f5776395e540b2c7c
- https://docs.docker.com/engine/release-notes/#20103
- https://github.com/moby/moby/releases/tag/v19.03.15
- https://github.com/moby/moby/releases/tag/v20.10.3
- https://security.gentoo.org/glsa/202107-23
- https://security.netapp.com/advisory/ntap-20210226-0005
- https://www.debian.org/security/2021/dsa-4865
