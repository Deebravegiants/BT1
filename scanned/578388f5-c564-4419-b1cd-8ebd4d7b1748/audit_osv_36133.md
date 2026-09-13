# [M] Division by Zero in iccDEV TIFF Image Reader

## Summary
Severity: Medium
Advisory: CVE-2026-21495
Aliases: GHSA-xhrm-79rg-5784
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21495
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to division by zero in the TIFF Image Reader. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21495.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-xhrm-79rg-5784
- https://nvd.nist.gov/vuln/detail/CVE-2026-21495
- https://github.com/InternationalColorConsortium/iccDEV/commit/10c34179a0332a869c2b46e305a9cd23a6311dfe
