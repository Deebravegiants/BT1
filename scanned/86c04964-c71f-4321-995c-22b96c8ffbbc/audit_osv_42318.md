# [M] Server-controlled `__next` URL is not checking cross-origin

## Summary
Severity: Medium
Advisory: CVE-2026-66773
Aliases: GHSA-hc5j-q32w-c25v
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-66773
Type: osv

## Details
A malicious or compromised OData service could disclose sensitive authentication information and inject untrusted data into the application, which may leads to a high impact on confidentiality and low impact on integrity and no impact on Availability.

## References
- https://url.sap/sapsecuritypatchday
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66773.json
- https://github.com/SAP/python-pyodata/security/advisories/GHSA-hc5j-q32w-c25v
- https://nvd.nist.gov/vuln/detail/CVE-2026-66773
