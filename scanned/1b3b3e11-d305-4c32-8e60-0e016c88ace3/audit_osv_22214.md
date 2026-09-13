# [H] Infinite loop in junrar

## Summary
Severity: High
Advisory: CVE-2022-23596
Aliases: GHSA-m6cj-93v6-cvr5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/CVE-2022-23596
Type: osv

## Details
Junrar is an open source java RAR archive library. In affected versions A carefully crafted RAR archive can trigger an infinite loop while extracting said archive. The impact depends solely on how the application uses the library, and whether files can be provided by malignant users. The problem is patched in 7.4.1. There are no known workarounds and users are advised to upgrade as soon as possible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23596.json
- https://github.com/junrar/junrar/security/advisories/GHSA-m6cj-93v6-cvr5
- https://nvd.nist.gov/vuln/detail/CVE-2022-23596
- https://github.com/junrar/junrar/issues/73
- https://github.com/junrar/junrar/commit/7b16b3d90b91445fd6af0adfed22c07413d4fab7
