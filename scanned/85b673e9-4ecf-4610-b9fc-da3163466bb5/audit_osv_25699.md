# [M] CVE-2023-42183

## Summary
Severity: Medium
Advisory: CVE-2023-42183
Aliases: GHSA-mgqj-hphf-9588
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-12-15
Source: https://osv.dev/vulnerability/CVE-2023-42183
Type: osv

## Details
lockss-daemon (aka Classic LOCKSS Daemon) before 1.77.3 performs post-Unicode normalization, which may allow bypass of intended access restrictions, such as when U+1FEF is converted to a backtick.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42183.json
- https://github.com/lockss/lockss-daemon/security/advisories/GHSA-mgqj-hphf-9588
- https://nvd.nist.gov/vuln/detail/CVE-2023-42183
