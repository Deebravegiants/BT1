# [C] Quiet uses insecure, inconsistent verification on local backend token

## Summary
Severity: Critical
Advisory: CVE-2025-53940
Aliases: GHSA-gpw8-w78h-xj67
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:N/SA:N)
Published: 2025-07-24
Source: https://osv.dev/vulnerability/CVE-2025-53940
Type: osv

## Details
Quiet is an alternative to team chat apps like Slack, Discord, and Element that does not require trusting a central server or running one's own. In versions 6.1.0-alpha.4 and below, Quiet's API for backend/frontend communication was using an insecure, not constant-time comparison function for token verification. This allowed for a potential timing attack where an attacker would try different token values and observe tiny differences in the response time (wrong characters fail faster) to guess the whole token one character at a time. This is fixed in version 6.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53940.json
- https://github.com/TryQuiet/quiet/security/advisories/GHSA-gpw8-w78h-xj67
- https://nvd.nist.gov/vuln/detail/CVE-2025-53940
- https://github.com/TryQuiet/quiet/issues/2820#issue-3021080269
- https://github.com/TryQuiet/quiet/pull/2928
