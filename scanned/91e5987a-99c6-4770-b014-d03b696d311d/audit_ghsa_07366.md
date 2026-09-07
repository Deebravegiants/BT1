# [H] PostgreSQL JDBC Driver: Silent channel-binding authentication downgrade via unsupported certificate algorithms

## Summary
Severity: High
Advisory: GHSA-j92g-9f8w-j867
CVE: CVE-2026-54291
CWE: CWE-636, CWE-757
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-j92g-9f8w-j867
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=42.7.4 <42.7.12

## Details
### Impact

`channelBinding=require` connections can be silently downgraded from `SCRAM-SHA-256-PLUS` (with channel binding) to plain `SCRAM-SHA-256` (without it), losing the man-in-the-middle protection the setting is meant to guarantee. An attacker who can intercept the TLS connection triggers the downgrade with a certificate whose signature algorithm has no `tls-server-end-point` channel-binding hash. Examples are `Ed25519`, `Ed448`, and post-quantum algorithms.

Two issues combine in releases 42.7.4 through 42.7.11:

1. The bundled `com.ongres.scram:scram-client` (3.1 or 3.2) returns an empty byte array instead of failing when it cannot derive the binding hash for such a certificate. This is the library issue tracked as [GHSA-p9jg-fcr6-3mhf](https://github.com/ongres/scram/security/advisories/GHSA-p9jg-fcr6-3mhf).
2. pgJDBC does not enforce `channelBinding=require` where it matters. `ScramAuthenticator` checks only that the server *advertised* a `-PLUS` mechanism; it neither rejects the empty binding nor checks that the *negotiated* mechanism uses channel binding. The connection therefore downgrades silently, and would do so even against a fixed `scram-client`, because the missing enforcement is in pgJDBC's own code.

Only connections that set `channelBinding=require` are affected. Under the default `prefer` policy, and under `allow` or `disable`, falling back to plain SCRAM is the documented behaviour. Releases before 42.7.4 are unaffected, because they do not support channel binding.

### Patches

Fixed in pgJDBC 42.7.12. pgJDBC now enforces channel binding in its own code, independently of the `scram-client` version:

- Under `channelBinding=require`, it fails the connection when no channel-binding data can be extracted from the server certificate, instead of passing an empty value to the SCRAM client. The error names the certificate signature algorithm.
- After negotiation, it requires the selected mechanism to use channel binding (a `-PLUS` mechanism) whenever `channelBinding=require` is set, regardless of how negotiation resolved.

Upgrade to 42.7.12 or later.

### Workarounds

No pgJDBC setting restores channel-binding enforcement on an affected release; upgrading is the fix.

If you cannot upgrade immediately, verify the server certificate at the TLS layer so that a man-in-the-middle cannot present a substitute certificate. Set `sslmode=verify-full` with a truststore that contains only your server's CA. This defence is independent of channel binding and blocks the same attacker. Connections that rely on `channelBinding=require` in place of certificate verification have no equivalent workaround and should upgrade.

### References

-  [GHSA-p9jg-fcr6-3mhf](https://github.com/ongres/scram/security/advisories/GHSA-p9jg-fcr6-3mhf) — the related `com.ongres.scram:scram-client` issue (root cause of the empty channel-binding value).
- `scram-client` 3.3 release (library fix): https://github.com/ongres/scram/releases/tag/3.3
- pgJDBC fix in 42.7.12: [commit](https://github.com/pgjdbc/pgjdbc/commit/77df98e4e66c12936ded3478a0954f6f580bad99)

## References
- https://github.com/pgjdbc/pgjdbc/security/advisories/GHSA-j92g-9f8w-j867
- https://nvd.nist.gov/vuln/detail/CVE-2026-54291
- https://github.com/pgjdbc/pgjdbc/commit/77df98e4e66c12936ded3478a0954f6f580bad99
- https://github.com/ongres/scram/releases/tag/3.3
- https://github.com/pgjdbc/pgjdbc
