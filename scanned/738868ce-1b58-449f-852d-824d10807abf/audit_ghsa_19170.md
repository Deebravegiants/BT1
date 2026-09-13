# [M] Keylime registrar is vulnerable to Denial-of-Service attack when updated to version 7.12.0

## Summary
Severity: Medium
Advisory: GHSA-9jxq-5x44-gx23
CVE: CVE-2025-1057
CWE: CWE-1287, CWE-704
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-9jxq-5x44-gx23
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=7.12.0 <7.12.1

## Details
### Impact
The Keylime `registrar` implemented more strict type checking on version 7.12.0. As a result, when updated to version 7.12.0, the `registrar` will not accept the format of the data previously stored in the database by versions  >= 7.8.0, raising an exception.

This makes the Keylime `registrar` vulnerable to a Denial-of-Service attack in an update scenario, as an attacker could populate the `registrar` database by creating multiple valid agent registrations with different UUIDs while the version is still < 7.12.0. Then, when the Keylime `registrar` is updated to the 7.12.0 version, any query to the database matching any of the entries populated by the attacker will result in failure.

### Patches
Users should upgrade to versions >= 7.12.1

### Workarounds
- Remove the registrar database and re-register all agents

### Credit

Reported by: Anderson Toshiyuki Sasaki/@ansasaki
Patched by: Anderson Toshiyuki Sasaki/@ansasaki

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-9jxq-5x44-gx23
- https://nvd.nist.gov/vuln/detail/CVE-2025-1057
- https://github.com/keylime/keylime/commit/e08b10d86c3717006774e787542c190e2ba24fc7
- https://access.redhat.com/security/cve/CVE-2025-1057
- https://bugzilla.redhat.com/show_bug.cgi?id=2343894
- https://github.com/advisories/GHSA-9jxq-5x44-gx23
- https://github.com/ansasaki/keylime/tree/base64_bytes
- https://github.com/keylime/keylime
- https://github.com/keylime/rust-keylime
- https://github.com/pypa/advisory-database/tree/main/vulns/keylime/PYSEC-2026-1488.yaml
- https://pypi.org/project/keylime
