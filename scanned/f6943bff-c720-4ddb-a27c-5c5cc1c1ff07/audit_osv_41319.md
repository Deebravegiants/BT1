# [M] Fixed predictable /tmp/ziptransformer work directory enables symlink pre-creation

## Summary
Severity: Medium
Advisory: CVE-2026-59311
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59311
Type: osv

## Details
A local unprivileged user on the same host can redirect all Zip/UnZip transformer output into a directory of their choosing by pre-creating /tmp/ziptransformer as a symlink before the application starts.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12

## References
- https://spring.io/security/cve-2026-59311
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59311.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59311
