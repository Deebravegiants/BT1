# [H] SpringBlade 2.7.3 < 5.0.0 Privilege Escalation via Exposed Feign Endpoint

## Summary
Severity: High
Advisory: CVE-2026-56100
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-56100
Type: osv

## Details
SpringBlade versions from 2.7.3 up to but not including 5.0.0 contain a privilege escalation vulnerability that allows authenticated attackers to create system administrator accounts by sending crafted POST requests to an unprotected internal Feign user-creation endpoint exposed via @RestController without authorization checks. Attackers can exploit the gateway's authentication filter, which only validates JWT parsing without verifying user roles or caller identity, and leverage a hardcoded JWT signing key embedded in publicly available JARs to forge tokens and escalate privileges from a low-privilege user to administrator, enabling cross-tenant data pollution and persistent backdoor access.

## References
- https://gitee.com/smallc/SpringBlade
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56100.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56100
- https://www.vulncheck.com/advisories/springblade-privilege-escalation-via-exposed-feign-endpoint
- https://github.com/chillzhuang/SpringBlade/commit/c69b9547c942c697da2f3ee6a9265b6004abd645
- https://github.com/chillzhuang/SpringBlade
- https://github.com/chillzhuang/SpringBlade/releases#release-v5.0.0
- https://gist.github.com/sud0why/e73405057dd7414a8c221ef17e0d0059#file-cve-2026-56100-springblade-authbypass-en-md
