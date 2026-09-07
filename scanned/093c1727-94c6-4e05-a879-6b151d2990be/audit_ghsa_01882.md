# [H] Unsafe inline XSS in pasting DOM element into chat

## Summary
Severity: High
Advisory: GHSA-2hfj-cxw7-g45p
CVE: CVE-2021-39183
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-2hfj-cxw7-g45p
Type: github-advisory

## Affected
- Go: `github.com/owncast/owncast` — affected >=0 <0.0.9

## Details
### Impact

Inline scripts are executed when Javascript is parsed via a paste action.

1. Open https://watch.owncast.online/
2. Copy and then paste `<img src=null onerror=alert('hello')>` into the
chat field.
3. An alert should pop up.

### Patches
```
    ⋮ 13 │    // Content security policy
    ⋮ 14 │    csp := []string{
    ⋮ 15 │        "script-src 'self' 'sha256-2HPCfJIJHnY0NrRDPTOdC7AOSJIcQyNxzUuut3TsYRY='",
    ⋮ 16 │        "worker-src 'self' blob:", // No single quotes around blob:
    ⋮ 17 │    }
```

Will be patched in 0.0.9 by blocking `unsafe-inline` Content Security Policy and specifying the `script-src`.  The `worker-src` is required to be set to `blob` for the video player.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [owncast/owncast](https://github.com/owncast/owncast/issues)
* Email us at [gabek@real-ity.com](mailto:gabek@real-ity.com)

## References
- https://github.com/owncast/owncast/security/advisories/GHSA-2hfj-cxw7-g45p
- https://nvd.nist.gov/vuln/detail/CVE-2021-39183
- https://github.com/owncast/owncast
