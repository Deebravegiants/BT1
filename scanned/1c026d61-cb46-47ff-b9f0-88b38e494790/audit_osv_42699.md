# [H] rsync 3.1.0 < 3.5.0 Access Control Bypass via DNS Resolution Failure

## Summary
Severity: High
Advisory: CVE-2026-70452
Aliases: GHSA-6692-28cx-wpqq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70452
Type: osv

## Details
rsync 3.1.0 before 3.5.0 contains an access control bypass vulnerability that allows remote attackers to circumvent hosts deny rules by inducing DNS resolution failures during hostname-based access control evaluation. When a DNS lookup for a hostname-based deny rule fails, the daemon skips the rule rather than defaulting to a deny decision, enabling attackers who can trigger DNS failures to bypass module-level IP access controls and gain unauthorized access to restricted module file trees.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70452.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-6692-28cx-wpqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-70452
- https://www.vulncheck.com/advisories/rsync-access-control-bypass-via-dns-resolution-failure
- https://github.com/RsyncProject/rsync
