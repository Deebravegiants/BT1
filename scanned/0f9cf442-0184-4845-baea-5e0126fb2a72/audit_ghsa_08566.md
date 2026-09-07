# [H] CloakBrowser: Unauthenticated path traversal via fingerprint parameter in cloakserve leads to arbitrary directory deletion

## Summary
Severity: High
Advisory: GHSA-mf33-gv72-w2h5
CVE: CVE-2026-45727
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-mf33-gv72-w2h5
Type: github-advisory

## Affected
- PyPI: `cloakbrowser` — affected >=0 <0.3.28

## Details
The `cloakserve` CDP multiplexer uses the user-supplied `fingerprint` query parameter directly as a filesystem path component when creating Chrome profile directories. An unauthenticated attacker who can reach the cloakserve port can supply a crafted `fingerprint` value containing path traversal sequences to resolve `user_data_dir` outside the configured `data_dir`. When Chrome fails to start or the process is cleaned up, `shutil.rmtree()` deletes the traversed path, resulting in arbitrary directory deletion.

Additionally, `cloakserve` bound to `0.0.0.0` by default, making it network-exposed.

### Impact

An attacker with network access to the cloakserve port can delete arbitrary directories accessible to the service user.

### Patches

Fixed in v0.3.28.

### Mitigations

- Upgrade to v0.3.28 or later
- Restrict network access to the cloakserve port

## References
- https://github.com/CloakHQ/CloakBrowser/security/advisories/GHSA-mf33-gv72-w2h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45727
- https://github.com/CloakHQ/CloakBrowser
