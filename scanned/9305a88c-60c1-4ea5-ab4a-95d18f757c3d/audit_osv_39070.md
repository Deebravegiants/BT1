# [H] Simple Machines Forum < 2.1.7 Authorization Confusion via Profile::load()

## Summary
Severity: High
Advisory: CVE-2026-43621
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-43621
Type: osv

## Details
Simple Machines Forum (SMF) through 2.1.7, fixed in commit 6f0dc61, contains an authorization state-confusion vulnerability in the profile loader that allows authenticated low-privileged users to gain administrator access by supplying multiple values for the user parameter. Attackers can exploit the mismatch between Profile::$member and User::$me->is_owner during sequential profile loading to be treated as the owner of an administrator profile, enabling unauthorized password changes and full account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43621.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43621
- https://www.vulncheck.com/advisories/simple-machines-forum-authorization-confusion-via-profile-load
- https://github.com/SimpleMachines/SMF/commit/6f0dc61958aa86a4b436a222f6176812ed5bbb95
- https://github.com/SimpleMachines/SMF
