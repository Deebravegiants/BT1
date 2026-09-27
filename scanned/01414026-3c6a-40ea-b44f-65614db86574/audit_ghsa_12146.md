# [M] openssl-encrypt has visible password in process list via --password CLI argument

## Summary
Severity: Medium
Advisory: GHSA-h3m5-p59h-x88p
CWE: CWE-256
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-h3m5-p59h-x88p
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

Passwords passed via the `--password` / `-p` CLI argument in `openssl_encrypt/modules/crypt_cli_subparser.py` at **lines 150-154** are visible to any user on the system via `ps aux` or `/proc/[pid]/cmdline`.

### Affected Code

```python
subparser.add_argument(
    "--password", "-p",
    help="Password (will prompt if not provided, or use CRYPT_PASSWORD environment variable)",
)
```

Similarly, `--keystore-password` exposes the keystore password.

### Impact

On multi-user systems, any user can observe the encryption password by listing processes. The `CRYPT_PASSWORD` environment variable alternative is also visible via `/proc/[pid]/environ` (though with slightly restricted access).

### Recommended Fix

- Document the security implications prominently
- Recommend interactive prompting (already supported) as the secure default
- Consider supporting password file descriptors (`--password-fd`) or reading from stdin
- Consider marking the argument as deprecated in favor of interactive prompting

### Fix

Fixed in commit `e78a366` on branch `releases/1.4.x` — added --password-file and --password-fd arguments; added OPENSSL_ENCRYPT_PASSWORD env var support; --password now emits deprecation warning.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-h3m5-p59h-x88p
- https://github.com/jahlives/openssl_encrypt/commit/e78a3666e4592f3538adaaa6be8f5f04356174db
- https://github.com/jahlives/openssl_encrypt
