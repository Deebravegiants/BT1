# [C] Azure AI Language Authoring Elevation of Privilege Vulnerability can Lead to RCE

## Summary
Severity: Critical
Advisory: GHSA-436v-jg82-p533
CVE: CVE-2026-21531
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-436v-jg82-p533
Type: github-advisory

## Affected
- PyPI: `azure-ai-language-conversations-authoring` — affected >=0 <1.0.0b4

## Details
Deserialization of untrusted data in the Azure AI Language Conversations Authoring client library for Python allows an unauthorized attacker to execute code over a network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-21531
- https://github.com/Azure/azure-sdk-for-python
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-21531
