# [H] Freighter mnemonic phrase may be accessed by Javascript through a private API

## Summary
Severity: High
Advisory: CVE-2023-40580
Aliases: GHSA-vqr6-hwg2-775w
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2023-08-25
Source: https://osv.dev/vulnerability/CVE-2023-40580
Type: osv

## Details
Freighter is a Stellar chrome extension. It may be possible for a malicious website to access the recovery mnemonic phrase when the Freighter wallet is unlocked. This vulnerability impacts access control to the mnemonic recovery phrase. This issue was patched in version 5.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40580.json
- https://github.com/stellar/freighter/security/advisories/GHSA-vqr6-hwg2-775w
- https://nvd.nist.gov/vuln/detail/CVE-2023-40580
- https://github.com/stellar/freighter/commit/81f78ba008c41ce631a3d0f9e4449f4bbd90baee
- https://github.com/stellar/freighter/pull/948
