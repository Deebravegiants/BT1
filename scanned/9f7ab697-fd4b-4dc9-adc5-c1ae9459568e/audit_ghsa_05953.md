# [H] Nx: Zip-Slip in the self-hosted remote cache

## Summary
Severity: High
Advisory: GHSA-vp3h-ghgh-jr7g
CVE: CVE-2026-71476
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-vp3h-ghgh-jr7g
Type: github-advisory

## Affected
- npm: `nx` — affected >=20.8.0 <22.7.7
- npm: `@nx/s3-cache` — affected >=0
- npm: `@nx/gcs-cache` — affected >=0
- npm: `@nx/azure-cache` — affected >=0
- npm: `@nx/shared-fs-cache` — affected >=0
- npm: `@nx/powerpack-s3-cache` — affected >=0
- npm: `@nx/powerpack-gcs-cache` — affected >=0
- npm: `@nx/powerpack-azure-cache` — affected >=0
- npm: `@nx/powerpack-shared-fs-cache` — affected >=0
- npm: `nx` — affected >=23.0.0 <23.0.2

## Details
## Summary

The Nx **self-hosted HTTP remote cache** extracts downloaded cache artifacts without constraining where files are written. A malicious — or on-path (MITM) — remote cache server can return a crafted tar archive whose entries escape the cache directory and write to arbitrary locations on the machine running Nx. This arbitrary file write can be escalated to remote code execution. The directly exploitable issue is the self-hosted HTTP remote cache.

## Affected Packages

> [!IMPORTANT]
> **Nx's default local cache and Nx Cloud are NOT affected.** The default local cache and Nx Cloud use separate cache retrieval and extraction mechanisms that does not have this vulnerability. Only workspaces that use a self-hosted remote cache (`NX_SELF_HOSTED_REMOTE_CACHE_SERVER`, `@nx/s3-cache`, etc.) are affected.

Two self-hosted cache surfaces are affected:

1. **The built-in HTTP remote cache** (`NX_SELF_HOSTED_REMOTE_CACHE_SERVER`, in `nx`) — **fixed** in the patched release.
2. **The self-hosted cache packages** — `@nx/s3-cache`, `@nx/gcs-cache`, `@nx/azure-cache`, `@nx/shared-fs-cache` (and their `@nx/powerpack-*` predecessors) — the same flaw in their own extractor. **Deprecated** (CVE-2025-36852) and not patched; migrate off (see Remediation).

The shared step that copies cached outputs into the workspace was also part of the exposure and is hardened in the patched `nx` release.

## Remediation

**Upgrade to Nx `22.7.7` or `23.0.2` (or later).** The patched extractor is a drop-in — no configuration change is required.

### If you use the S3, GCS, Azure, or shared-filesystem cache packages

`@nx/s3-cache`, `@nx/gcs-cache`, `@nx/azure-cache`, and `@nx/shared-fs-cache` (and their `@nx/powerpack-*` predecessors) are separately versioned packages and are **already deprecated** (see CVE-2025-36852). Upgrading `nx` hardens the shared restore step, but it does not fully secure these packages. The remediation for them is to **migrate off** — to Nx Cloud or the self-hosted OpenAPI/HTTP remote cache — per the deprecation guidance: https://nx.dev/docs/reference/deprecated/self-hosted-cache-packages

## Details

When Nx retrieves an artifact from the self-hosted HTTP remote cache, it downloads a gzipped tar archive and extracts it. The extractor joined each untrusted tar entry name directly onto the output directory and unpacked it with `tar`'s **unguarded** `Entry::unpack()`, which performs no containment check:

```rust
// vulnerable
let path_on_disk = output_dir.join(entry_path); // entry_path is attacker-controlled
fs::create_dir_all(path_on_disk.parent()…)?;
entry.unpack(&path_on_disk)?;
```

In addition, restore now copies **only** the declared task outputs (never the whole cache directory), confined to the workspace root; parent directories are realized as real directories so a write can never traverse a symlink; declared outputs that resolve outside the workspace are rejected; and the malformed-input cases return errors instead of panicking.

## References

- Fix: https://github.com/nrwl/nx/pull/36116 (merged)
- TLS-verification warning follow-up: https://github.com/nrwl/nx/pull/36132 (merged)
- Vulnerable extractor introduced in Nx 20.8.0: https://github.com/nrwl/nx/pull/30593

## Credits

- **Lidor B.**, Novee Security — Reporter
- **Assaf Levkovich**, Novee Security — Reporter

## References
- https://github.com/nrwl/nx/security/advisories/GHSA-vp3h-ghgh-jr7g
- https://github.com/nrwl/nx/pull/36116
- https://github.com/nrwl/nx/commit/2b20c2da39d263c32ae05767577589481a309fee
- https://github.com/nrwl/nx/commit/a82807621e4176e37909d2c1afede661b45cc30
- https://github.com/nrwl/nx/commit/ad296578fe980a4aad66f8af0add21f6ddf907d9
- https://github.com/nrwl/nx
