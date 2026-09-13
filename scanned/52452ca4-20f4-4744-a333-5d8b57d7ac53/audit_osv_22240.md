# [H] CVE-2022-23952

## Summary
Severity: High
Advisory: CVE-2022-23952
Aliases: GHSA-fchm-5w2v-qfm8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-23952
Type: osv

## Details
In Keylime before 6.3.0, current keylime installer installs the keylime.conf file, which can contain sensitive data, as world-readable.

## References
- https://seclists.org/oss-sec/2022/q1/101
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23952.json
- https://github.com/keylime/keylime/security/advisories/GHSA-fchm-5w2v-qfm8
- https://nvd.nist.gov/vuln/detail/CVE-2022-23952
- https://github.com/keylime/keylime/commit/883085d6a4bcea3012729014d5b8e15ecd65fc7c
