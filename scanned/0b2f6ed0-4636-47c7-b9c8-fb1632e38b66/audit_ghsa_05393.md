# [M] go-tuf Path Traversal in TAP 4 Multirepo Client Allows Arbitrary File Write via Malicious Repository Names

## Summary
Severity: Medium
Advisory: GHSA-jqc5-w2xx-5vq4
CVE: CVE-2026-24686
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-jqc5-w2xx-5vq4
Type: github-advisory

## Affected
- Go: `github.com/theupdateframework/go-tuf/v2` — affected >=0 <2.4.1

## Details
# Security Vulnerability: Path Traversal in TAP 4 Multirepo Client

## Summary

go-tuf's TAP 4 Multirepo Client uses the map file repository name string (`repoName`) as a filesystem path component when selecting the local metadata cache directory. If an application accepts a map file from an untrusted source, an attacker can supply a `repoName` containing traversal (e.g., `../escaped-repo`) and cause go-tuf to create directories and write the root metadata file outside the intended `LocalMetadataDir` cache base, within the running process's filesystem permissions.

## Affected Component

| Field | Value |
|-------|-------|
| **File** | `metadata/multirepo/multirepo.go` |
| **Function** | `(*MultiRepoClient) initTUFClients() error` |
| **Callsite** | `metadataDir := filepath.Join(client.Config.LocalMetadataDir, repoName)` (around line 129 at the pinned commit) |

## Impact

When the TAP 4 map file content is attacker-controlled, this enables arbitrary file write relative to the process permissions (via metadata persistence during client initialization). This can be used to overwrite files writable by the process (for example, configuration files in writable directories) and may enable further compromise depending on the deployment environment.

> **Note:** Exploitability is deployment-dependent. If the map file is always local and trusted (not attacker-controlled), this reduces to a misconfiguration risk rather than a remotely triggerable issue.

## Attacker Model

- Attacker can cause the application to load a TAP 4 map file whose `repositories` keys are attacker-controlled (for example: fetched from a URL, supply-chain substituted, or otherwise attacker-influenced input).
- Local caching is enabled (`DisableLocalCache=false`) and the configured `LocalMetadataDir` is writable by the running process.

**Claim Ceiling:** HIGH when the map file is attacker-controlled; if the map file is always local and trusted, this is closer to a configuration footgun and likely lands as MEDIUM/LOW.

| Field | Value |
|-------|-------|
| **Affected Versions** | ≤ 2.4.0 |
| **Verified On** | Commit `bde5f18dc95dfac365fc452ee4e278e5fd66d4b4` (tag v2.4.0) |

> **Note:** First affected version has not been bisected.

## Reproduction

Attachments include `poc.zip` with:
- `canonical.log` (contains `[CALLSITE_HIT]`, `[PROOF_MARKER]`)
- `control.log` (contains `[CALLSITE_HIT]`, `[NC_MARKER]`, does not contain `[PROOF_MARKER]`)
- `fix.patch` (minimal validation sketch)

**Expected:** Multirepo repository names are treated as identifiers; a TAP 4 map file containing traversal or absolute paths is rejected (or safely normalized so that all writes stay under `LocalMetadataDir`).

**Actual:** A traversal `repoName` escapes `LocalMetadataDir` and go-tuf persists `root.json` under the escaped path during initialization.

### Run Local Repro

```bash
rm -rf _poc
mkdir -p _poc
unzip -q -o poc.zip -d _poc
cd _poc/poc
make canonical
make control
```

## Workarounds

1. Treat TAP 4 map files as trusted configuration only (do not fetch from untrusted sources).
2. Validate repo names before passing the map file to go-tuf (reject absolute paths, path separators, and traversal components like `.` / `..`).
3. If acceptable for the application, disable local caching to avoid writing metadata to disk (`DisableLocalCache=true`).

## Suggested Remediation

Validate multirepo repository names as identifiers (not paths) before using them in `filepath.Join`. Reject:
- Absolute paths
- Path separators (`/` and `\`)
- Traversal components (`.` and `..`)

If it is important to accept a wider set of repo names, a safer alternative is to map repo names to a stable, validated directory name (for example via encoding or hashing) and to ensure all writes stay under the cache base directory.

## Triage Questions

1. Is the TAP 4 map file expected to ever be fetched from untrusted sources in supported deployments?
2. Should invalid repo names be treated as a hard error (reject initialization), or as a soft error (skip that repository entry)?

## Attachments

- [poc.zip](https://github.com/user-attachments/files/24849854/poc.zip)
- [addendum.md](https://github.com/user-attachments/files/24849855/addendum.md)
- [e2e.zip](https://github.com/user-attachments/files/24849856/e2e.zip)
- [PR_DESCRIPTION.md](https://github.com/user-attachments/files/24849858/PR_DESCRIPTION.md)

---

*Reported by: Oleh*

## References
- https://github.com/theupdateframework/go-tuf/security/advisories/GHSA-jqc5-w2xx-5vq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24686
- https://github.com/theupdateframework/go-tuf/commit/d361e2ea24e427581343dee5c7a32b485d79fcc0
- https://github.com/theupdateframework/go-tuf
