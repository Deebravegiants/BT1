# [C] Improper Privilege Management in sap-xssec

## Summary
Severity: Critical
Advisory: GHSA-6mjg-37cp-42x5
CVE: CVE-2023-50423
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-6mjg-37cp-42x5
Type: github-advisory

## Affected
- PyPI: `sap-xssec` — affected >=0 <4.1.0

## Details
### Impact

SAP BTP Security Services Integration Library ([Python] sap-xssec) allows under certain conditions an escalation of privileges. On successful exploitation, an unauthenticated attacker can obtain arbitrary permissions within the application.

### Patches
Upgrade to patched version >= 4.1.0
We always recommend to upgrade to the latest released version.

### Workarounds
No workarounds

### References
https://www.cve.org/CVERecord?id=CVE-2023-50423

## References
- https://github.com/SAP/cloud-pysec/security/advisories/GHSA-6mjg-37cp-42x5
- https://nvd.nist.gov/vuln/detail/CVE-2023-50423
- https://github.com/SAP/cloud-pysec/commit/d90c9e0733fa9af68bd8ea0b1cf023cf482163ef
- https://blogs.sap.com/2023/12/12/unveiling-critical-security-updates-sap-btp-security-note-3411067
- https://github.com/SAP/cloud-pysec
- https://github.com/pypa/advisory-database/tree/main/vulns/sap-xssec/PYSEC-2023-261.yaml
- https://me.sap.com/notes/3411067
- https://pypi.org/project/sap-xssec
- https://www.sap.com/documents/2022/02/fa865ea4-167e-0010-bca6-c68f7e60039b.html
