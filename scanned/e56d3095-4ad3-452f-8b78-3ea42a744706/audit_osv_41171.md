# [C] Orkes Conductor 3.21.21 < 3.30.2 Unauthenticated RCE via GraalVM Script Evaluators

## Summary
Severity: Critical
Advisory: CVE-2026-58138
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58138
Type: osv

## Details
Orkes Conductor 3.21.21 before 3.30.2 contains an unauthenticated remote code execution vulnerability that allows remote attackers to execute arbitrary OS commands by submitting inline workflow definitions containing malicious JavaScript or Python expressions to the workflow API endpoint prior to authentication. Attackers can exploit unsandboxed GraalVM evaluators configured with HostAccess.ALL or allowAllAccess(true) through INLINE, LAMBDA, DO_WHILE, and SWITCH task types to invoke arbitrary system commands via Java reflection or direct subprocess calls.

## References
- https://www.cve.org/CVERecord?id=CVE-2025-26074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58138.json
- https://github.com/conductor-oss/conductor/releases/tag/v3.30.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-58138
- https://www.vulncheck.com/advisories/orkes-conductor-unauthenticated-rce-via-graalvm-script-evaluators
- https://github.com/conductor-oss/conductor/commit/87a7d96aabbb706d6e84f812b93da5165028d18f
- https://github.com/conductor-oss/conductor/commit/c691e35e768caeb802c9f06ecdd9674c80081af1
- https://github.com/conductor-oss/conductor
