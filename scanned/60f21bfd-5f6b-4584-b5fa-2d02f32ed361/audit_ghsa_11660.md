# [M] openssl-encrypt: Dynamic .so loading for Whirlpool uses broad glob pattern without integrity verification

## Summary
Severity: Medium
Advisory: GHSA-j48q-4c78-rhf9
CWE: CWE-427
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-j48q-4c78-rhf9
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
## Severity: HIGH

### Summary

The Whirlpool hash implementation in `openssl_encrypt/modules/registry/hash_registry.py` at **lines 570-589** uses glob patterns to find `.so` modules in site-packages and loads the first match via `importlib` without verifying module integrity.

### Affected Code

```python
for site_pkg in site.getsitepackages():
    pattern = os.path.join(site_pkg, "whirlpool*py313*.so")
    py313_modules = glob.glob(pattern)
    if py313_modules:
        module_path = py313_modules[0]  # Takes first match
        loader = ExtensionFileLoader("whirlpool", module_path)
        spec = importlib.util.spec_from_file_location("whirlpool", module_path, loader=loader)
        whirlpool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(whirlpool_module)
```

### Impact

The glob pattern `"whirlpool*py313*.so"` is broad and takes the first match without verifying:
- File hash/signature
- File ownership/permissions
- Whether it's a legitimate module

If an attacker can place a malicious `.so` file matching this pattern in any site-packages directory, it will be loaded and native code executed.

### Recommended Fix

- Verify the module's integrity (hash or signature) before loading
- Use a specific filename rather than a glob pattern
- Check file permissions and ownership

### Fix

Fixed in commit `963d0d1` on branch `releases/1.4.x` — added os.path.realpath() to resolve symlinks and validation that found .so files are within known site-packages directories before loading.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-j48q-4c78-rhf9
- https://github.com/jahlives/openssl_encrypt/commit/963d0d1278b722ea134272f9df65fddcd3e6ab47
- https://github.com/jahlives/openssl_encrypt
