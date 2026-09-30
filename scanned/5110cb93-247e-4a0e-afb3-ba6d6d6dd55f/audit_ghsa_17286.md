# [M] Weblate has Systematic User and Project Enumeration via Broken Authorization in REST API (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-3pmh-24wp-xpf4
CVE: CVE-2025-67715
CWE: CWE-284, CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-3pmh-24wp-xpf4
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.15

## Details
### Impact

It was possible to retrieve user notification settings or list all users via API.

### Patches

* https://github.com/WeblateOrg/weblate/pull/17256

### References

Thanks to Hector Ruiz Ruiz & NaxusAI for responsibly disclosing this vulnerability to Weblate.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-3pmh-24wp-xpf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-67715
- https://github.com/WeblateOrg/weblate/pull/17256
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2025-233.yaml
