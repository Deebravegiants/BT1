# [C] rsync < 3.5.0 Command Injection via Multiple Code Paths

## Summary
Severity: Critical
Advisory: CVE-2026-53790
Aliases: GHSA-5hcf-7xxm-rmqq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53790
Type: osv

## Details
rsync before 3.5.0 contains multiple command and argument injection vulnerabilities that allow attackers to execute arbitrary commands by supplying malicious input through several code paths, including the RSYNC_CONNECT_PROG environment variable, daemon hooks, the rsync-ssl wrapper, and remote-shell command newline injection. Attackers can inject shell metacharacters or newline characters into unsanitized user-supplied values such as hostnames and hostspecs to execute arbitrary commands under the privileges of the rsync process or the invoking user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53790.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-5hcf-7xxm-rmqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-53790
- https://www.vulncheck.com/advisories/rsync-command-injection-via-multiple-code-paths
- https://github.com/RsyncProject/rsync
