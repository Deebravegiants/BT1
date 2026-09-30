# [H] Ipa: freeipa: unauthenticated dos in `/ipa/migration/migration.py` via unbounded request body read

## Summary
Severity: High
Advisory: CVE-2026-73197
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-73197
Type: osv

## Details
A flaw was found in FreeIPA. A remote, unauthenticated attacker can exploit this vulnerability by sending oversized form POST requests to the `/ipa/migration/migration.py` endpoint. This can force the migration handler to read attacker-controlled request bodies fully into memory, leading to increased memory usage, slower request handling, and potential service disruption or denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-73197
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73197.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73197
- https://bugzilla.redhat.com/show_bug.cgi?id=2474697
