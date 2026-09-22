# [C] OpenHuman desktop agent shell tool sandbox bypass leads to arbitrary command execution

## Summary
Severity: Critical
Advisory: CVE-2026-55743
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55743
Type: osv

## Details
The shell tool command allowlist in the SecurityPolicy of OpenHuman desktop agent through 0.54.0 (default Supervised security policy) can be bypassed to execute arbitrary OS commands with the privileges of the desktop user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55743.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55743
- https://github.com/tinyhumansai/openhuman/commit/60050aa09a870f53ed7e4cd40ed41fd2860329e7
- https://github.com/tinyhumansai/openhuman
- https://github.com/tinyhumansai/openhuman/blob/v0.53.49-staging/src/openhuman/security/policy.rs
