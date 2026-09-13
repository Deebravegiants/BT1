# [M] NocoDB: Path Traversal via SQLite Source Filename

## Summary
Severity: Medium
Advisory: GHSA-wvqj-9wv4-7ff5
CVE: CVE-2026-47385
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-wvqj-9wv4-7ff5
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
An authenticated user with base-create permission can attach a SQLite source pointing at
an arbitrary file on the NocoDB host, including NocoDB's own internal databases.

### Details
The SQLite client and the base/integration create services accepted a caller-supplied
filename and passed it to `fs.exists` and `fs.open('w')` without restricting the location.
A user could point a source at `noco.db`, at a tenant database under `nc_minimal_dbs/`,
or at any writable path the NocoDB process can reach, and then read or overwrite its
contents through the regular table APIs.

### Impact
Disclosure and modification of NocoDB internal state, of other tenants' databases, and
of any file the NocoDB process can read or write. Authentication and base-create
permission are required.

### Credit
This issue was reported by [@Mouhebbenelwafi](https://github.com/Mouhebbenelwafi).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-wvqj-9wv4-7ff5
- https://nvd.nist.gov/vuln/detail/CVE-2026-47385
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
