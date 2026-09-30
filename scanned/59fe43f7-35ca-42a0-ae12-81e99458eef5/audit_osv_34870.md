# [H] Inside Track / Entropy Derby Timelock Encryption Bypassed via Pre-Computed VDF Output Leakage

## Summary
Severity: High
Advisory: CVE-2025-65951
Aliases: GHSA-pm54-f847-w4mh
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-65951
Type: osv

## Details
Inside Track / Entropy Derby is a research-grade horse-racing betting engine. Prior to commit 2d38d2f, the VDF-based timelock encryption system fails to enforce sequential delay against the betting operator. Bettors pre-compute the entire Wesolowski VDF and include vdfOutputHex in their encrypted bet ticket, allowing the house to decrypt immediately using fast proof verification instead of expensive VDF evaluation. This issue has been patched via commit 2d38d2f.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65951.json
- https://github.com/mescuwa/entropy-derby/security/advisories/GHSA-pm54-f847-w4mh
- https://nvd.nist.gov/vuln/detail/CVE-2025-65951
- https://github.com/mescuwa/entropy-derby/commit/2d38d2f16bbb3b4240698148f80d8c5202725c77
