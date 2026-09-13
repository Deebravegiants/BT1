# [M] pnpm: reserved bin name deletes PNPM_HOME during global remove

## Summary
Severity: Medium
Advisory: CVE-2026-55699
Aliases: GHSA-4gxm-v5v7-fqc4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55699
Type: osv

## Details
pnpm is a package manager. Prior to 10.34.2 and 11.5.3, Manifest bin object keys such as "", ".", and ".." passed pnpm's bin-name guard. When a malicious package was installed globally, later global remove, update, or add-replacement flows could re-derive those names from the installed manifest and pass path.join(globalBinDir, binName) to removeBin. For "." this targets the global bin directory; for ".." this targets its parent. This vulnerability is fixed in 10.34.2 and 11.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55699.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-4gxm-v5v7-fqc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55699
