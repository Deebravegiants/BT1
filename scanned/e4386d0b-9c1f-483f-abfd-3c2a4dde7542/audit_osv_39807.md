# [H] Pathling: $import-pnp operation enables authenticated SSRF, credential leakage, and warehouse data poisoning

## Summary
Severity: High
Advisory: CVE-2026-47664
Aliases: GHSA-69wc-hrxh-5528
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-47664
Type: osv

## Details
Pathling is a set of tools that make it easier to use FHIR and clinical terminology within health data analytics. Prior to version 2.0.0 of Pathling Server, the `$import-pnp` operation in Pathling Server accepts a caller-supplied `exportUrl` and uses it as the remote FHIR Bulk Export endpoint without constraining it to a trusted source. When PNP credentials are configured, Pathling builds a credentialed bulk-export client targeting the caller-chosen host, downloads manifest-selected files, and then reclassifies those staged files as trusted local `file://` imports - bypassing the configured `allowableSources` allowlist that protects the ordinary `$import` operation. This is fixed in Pathling Server 2.0.0. As a workaround, disable the `$import-pnp` operation (`pathling.operations.importPnpEnabled=false`) or do not configure PNP credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47664.json
- https://github.com/aehrc/pathling/security/advisories/GHSA-69wc-hrxh-5528
- https://nvd.nist.gov/vuln/detail/CVE-2026-47664
