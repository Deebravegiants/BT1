# [M] Gitingest Prefix-Based Git Host Check Enables Request Forgery and Token Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-82289
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82289
Type: osv

## Details
Gitingest through 0.3.1 fails to properly validate hostnames in _validate_host, accepting any host with a git., gitlab., or github. prefix regardless of known-hosts list membership. Attackers can submit URLs with attacker-controlled hostnames to trigger outbound connections to arbitrary hosts and disclose GitHub personal access tokens via HTTP basic credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82289.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82289
- https://www.vulncheck.com/advisories/gitingest-prefix-based-git-host-check-enables-request-forgery-and-token-disclosure
- https://github.com/coderamp-labs/gitingest/issues/592
- https://github.com/coderamp-labs/gitingest
- https://github.com/coderamp-labs/gitingest/blob/4e259a02fe72115bee538271622f1234a81c8e1a/src/gitingest/utils/git_utils.py
- https://github.com/coderamp-labs/gitingest/blob/4e259a02fe72115bee538271622f1234a81c8e1a/src/gitingest/utils/query_parser_utils.py
