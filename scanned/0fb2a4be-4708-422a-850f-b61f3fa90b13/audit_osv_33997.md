# [M] giscus allows unauthorized discussion creation

## Summary
Severity: Medium
Advisory: CVE-2025-53532
Aliases: GHSA-w6vg-v24f-4vm3
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53532
Type: osv

## Details
giscus is a commenting system powered by GitHub Discussions. A bug in giscus' discussions creation API allowed an unauthorized user to create discussions on any repository where giscus is installed. This affects the server-side part of giscus, which is provided via http://giscus.app or your own self-hosted service. This vulnerability is fixed by the c43af7806e65adfcf4d0feeebef76dc36c95cb9a and 4b9745fe1a326ce08d69f8a388331bc993d19389 commits.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53532.json
- https://github.com/giscus/giscus/security/advisories/GHSA-w6vg-v24f-4vm3
- https://nvd.nist.gov/vuln/detail/CVE-2025-53532
- https://github.com/giscus/giscus/commit/4b9745fe1a326ce08d69f8a388331bc993d19389
- https://github.com/giscus/giscus/commit/c43af7806e65adfcf4d0feeebef76dc36c95cb9a
