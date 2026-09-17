# [M] nextflow auth login command has incorrect default permissions

## Summary
Severity: Medium
Advisory: GHSA-92qf-fcph-v5wr
CVE: CVE-2026-48722
CWE: CWE-276, CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-92qf-fcph-v5wr
Type: github-advisory

## Affected
- Maven: `io.nextflow:nextflow` — affected >=25.09.2-edge <25.10.6
- Maven: `io.nextflow:nextflow` — affected >=26.00.0-edge <26.04.3

## Details
### Impact

`nextflow auth login` persists Seqera Platform OIDC tokens to `${NXF_HOME:-~/.nextflow}/seqera-auth.config`. The file is created via Java NIO without specifying file permissions, so under the default `umask 022` it lands at mode `0644` (world-readable).

On a multi-user POSIX host — typically an HPC login node, shared workstation, or jump host — any local user able to traverse the victim's home directory can read the file and obtain a valid Platform bearer token, enabling impersonation against Seqera Platform within the token's scope.

Single-user systems and headless CI runners, which do not invoke the interactive login flow, are not affected.

Affected versions:  `25.09.2-edge` through `26.04.1`.
  
### Patches

Fixed in `<PATCHED_VERSION>`. The patched code applies mode `0600` to `seqera-auth.config` immediately after writing it, and re-applies on every subsequent login so any pre-existing world-readable copy left by an earlier version is tightened.

Tokens previously stored in the file must be treated as disclosed. After upgrading, run `nextflow auth logout`, revoke the token in the Seqera Platform UI, and run `nextflow auth login` again.

### Workarounds
  
Restrict the file and its parent directory:

`chmod 600 "${NXF_HOME:-$HOME/.nextflow}/seqera-auth.config"`
`chmod 700 "${NXF_HOME:-$HOME/.nextflow}"`

Alternatively, supply the Platform token via the `TOWER_ACCESS_TOKEN` environment variable instead of running `nextflow auth login`.

### References
  
  - https://cwe.mitre.org/data/definitions/276.html

## References
- https://github.com/nextflow-io/nextflow/security/advisories/GHSA-92qf-fcph-v5wr
- https://github.com/nextflow-io/nextflow
