# [H] Undertow vulnerable to memory exhaustion due to buffer leak

## Summary
Severity: High
Advisory: GHSA-fj7c-vg2v-ccrm
CVE: CVE-2021-3690
CWE: CWE-400, CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-fj7c-vg2v-ccrm
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.40
- Maven: `io.undertow:undertow-core` — affected >=2.2.0 <2.2.10

## Details
Buffer leak on incoming WebSocket PONG message(s) in Undertow before 2.0.40 and 2.2.10 can lead to memory exhaustion and allow a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3690
- https://github.com/undertow-io/undertow/commit/c7e84a0b7efced38506d7d1dfea5902366973877
- https://access.redhat.com/security/cve/CVE-2021-3690
- https://access.redhat.com/security/cve/cve-2021-3690#cve-cvss-v3
- https://bugzilla.redhat.com/show_bug.cgi?id=1991299
- https://github.com/undertow-io/undertow
- https://issues.redhat.com/browse/UNDERTOW-1935
- https://www.mend.io/vulnerability-database/CVE-2021-3690
