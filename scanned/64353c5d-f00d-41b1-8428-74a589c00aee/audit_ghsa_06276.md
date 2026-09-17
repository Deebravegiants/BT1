# [M] devpi-server may leak database contents

## Summary
Severity: Medium
Advisory: GHSA-m5pq-69xg-vcq3
CVE: CVE-2026-54723
CWE: CWE-304
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-m5pq-69xg-vcq3
Type: github-advisory

## Affected
- PyPI: `devpi-server` — affected >=0 <6.20.2

## Details
### Impact

If the replication protocol is enabled by using the ``primary`` (or deprecated ``master``) role for a server instance, then the ``+changelog`` URL route can be used to read the complete database content including password hashes, and the ids and salts of tokens from ``devpi-tokens`` by using a trivially modified GET request.

The leaked hashes use the ``argon2`` algorithm, so they are not immediately at risk by brute-force methods, but dictionary attacks are feasible. If a database leak could have happened, it is advised to change the passwords after a patched version or other mitigation is in place.

When ``devpi-tokens`` is in use, the quality of the server secret is important. It might be possible to derive the server secret if actual tokens are public by using similar techniques to finding the password for a hash. If a database leak could have happened and any tokens are public, it is advised to change the server secret.

Besides the information leak this can be used to produce significant CPU, IO and bandwidth usage depending on the database size.

### Patches

The logic bug causing this issue is fixed with devpi-server 6.20.2 and devpi-server 7.0.0b3.

### Workarounds

When replication isn't used the role can explicitly be set to ``standalone``.

If the server instance is exclusively served through ``nginx`` with the ``devpi-lockdown`` plugin, the request is redirected to the login form due to missing user information. There is no known exploit in this case.

## References
- https://github.com/devpi/devpi/security/advisories/GHSA-m5pq-69xg-vcq3
- https://github.com/devpi/devpi
