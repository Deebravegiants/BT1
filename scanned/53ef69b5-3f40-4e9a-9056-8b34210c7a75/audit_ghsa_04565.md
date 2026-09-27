# [C] ChromaDB has a code injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-36p7-vc44-83pf
CVE: CVE-2026-45833
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-36p7-vc44-83pf
Type: github-advisory

## Affected
- PyPI: `chromadb` — affected >=0.4.17

## Details
A code injection vulnerability in version 0.4.17 or later of the ChromaDB Python project allows an authenticated attacker to run arbitrary code on the server by sending a malicious model repository and trust_remote_code set to true in the /api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id} if they have the UPDATE_COLLECTION permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45833
- https://access.redhat.com/security/cve/CVE-2026-45833
- https://bugzilla.redhat.com/show_bug.cgi?id=2488430
- https://github.com/chroma-core/chroma
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45833.json
- https://www.hiddenlayer.com/sai-security-advisory/2026-06-chromadb-5
