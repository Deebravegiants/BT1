# [M] http4k: `DigestAuthProvider.verify` ignored configured algorithm and did not bind to request URI

## Summary
Severity: Medium
Advisory: GHSA-vxxm-wwqh-mh47
CVE: CVE-2026-54147
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-vxxm-wwqh-mh47
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-security-digest` — affected >=6.0.0.0 <6.50.0.0
- Maven: `org.http4k:http4k-security-digest` — affected >=5.0.0.0 <5.42.0.0
- Maven: `org.http4k:http4k-security-digest` — affected >=0

## Details
### Impact

An issue in `DigestAuthProvider.verify`:

 **Algorithm silently forced to MD5.** The configured `algorithm` parameter was ignored — every verification used MD5 regardless of configuration. Deployments believing they were running SHA-256 Digest auth were silently inheriting MD5's collision weaknesses, including documented attack paths against Digest schemes that rely on the hash being collision-resistant.

**Who is affected:** any application using `http4k-security-digest` for HTTP Digest authentication. The bug has been present since `DigestAuthProvider` was introduced (commit `8a52b615b1`, 2021).

### Patches

| Line | Fixed in | Edition |
|------|----------|---------|
| v6.x (Community) | **6.50.0.0** | Community |
| v5.x (LTS) | **5.42.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) (if Digest auth is present in your v5.x line) |
| v4.x (LTS) | **4.51.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) (if Digest auth is present in your v4.x line) |

The fix:
- Hashes with the configured `algorithm` instead of hardcoded MD5.

### Workarounds

For deployments that cannot upgrade immediately:
- **Algorithm gap:** do not rely on `algorithm` configuration; assume MD5 is in use and treat the Digest credentials as low-trust.

### References

- Vulnerability first present: [`8a52b615b1`](https://github.com/http4k/http4k/commit/8a52b615b1)
- Algorithm fix: [`65d23d99fc`](https://github.com/http4k/http4k/commit/65d23d99fc)
- Fix release: [v6.50.0.0](https://github.com/http4k/http4k/releases/tag/6.50.0.0)
- Background: [RFC 7616 — HTTP Digest Access Authentication](https://datatracker.ietf.org/doc/html/rfc7616)

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-vxxm-wwqh-mh47
- https://github.com/http4k/http4k/commit/65d23d99fc
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/releases/tag/6.50.0.0
