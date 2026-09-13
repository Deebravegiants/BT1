# [M] Weblate's over‑permissive webhook endpoint enables mass repository updates and component enumeration

## Summary
Severity: Medium
Advisory: GHSA-pj86-258h-qrvf
CVE: CVE-2025-67492
CWE: CWE-1286
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-pj86-258h-qrvf
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.15

## Details
### Impact

It was possible to trigger repository updates for many repositories via a crafted webhook payload.

### Patches

* https://github.com/WeblateOrg/weblate/pull/17221

### Workarounds

Disabling webhooks completely using ENABLE_HOOKS avoids this vulnerability.

### References

Thanks to Hector Ruiz Ruiz & NaxusAI for responsibly disclosing this vulnerability to us.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-pj86-258h-qrvf
- https://nvd.nist.gov/vuln/detail/CVE-2025-67492
- https://github.com/WeblateOrg/weblate/pull/17221
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2025-232.yaml
