# [H] Volcano Scheduler Denial of Service via Unbounded Response from Elastic Service/extender Plugin

## Summary
Severity: High
Advisory: GHSA-hg79-fw4p-25p8
CVE: CVE-2025-32777
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H (CVSS_V4)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-hg79-fw4p-25p8
Type: github-advisory

## Affected
- Go: `volcano.sh/volcano` — affected >=0 <1.9.1
- Go: `volcano.sh/volcano` — affected >=1.10.0-alpha.0 <1.10.2
- Go: `volcano.sh/volcano` — affected >=1.11.0-network-topology-preview.0 <1.11.0-network-topology-preview.3
- Go: `volcano.sh/volcano` — affected >=1.11.0 <1.11.2
- Go: `volcano.sh/volcano` — affected >=1.12.0-alpha.0 <1.12.0-alpha.2

## Details
### Impact
This issue allows an attacker who has compromised either the Elastic service or the extender plugin to cause denial of service of the scheduler. This is a privilege escalation, because Volcano users may run their Elastic service and extender plugins in separate pods or nodes from the scheduler. In the Kubernetes security model, node isolation is a security boundary, and as such an attacker is able to cross that boundary in Volcano's case if they have compromised either the vulnerable services or the pod/node in which they are deployed.  The scheduler will become unavailable to other users and workloads in the cluster. The scheduler will either crash with an unrecoverable OOM panic or freeze while consuming excessive amounts of memory.

### Workarounds
No

## References
- https://github.com/volcano-sh/volcano/security/advisories/GHSA-hg79-fw4p-25p8
- https://nvd.nist.gov/vuln/detail/CVE-2025-32777
- https://github.com/volcano-sh/volcano/commit/45a4347471a5254121d10afef04c6732095fa398
- https://github.com/volcano-sh/volcano/commit/7103c18de19821cd278f949fa24c13da350a8c5d
- https://github.com/volcano-sh/volcano/commit/735842af59b9be0da5090677db7693c98a798b2a
- https://github.com/volcano-sh/volcano/commit/7c0ea53fa3cfa7a05b5fba7a8af7bfe88adc41c3
- https://github.com/volcano-sh/volcano/commit/d687f75a11fa36f37b54e4b6ff8e49bc0a3ca6b4
- https://github.com/volcano-sh/volcano
- https://github.com/volcano-sh/volcano/releases/tag/v1.10.2
- https://github.com/volcano-sh/volcano/releases/tag/v1.11.0-network-topology-preview.3
- https://github.com/volcano-sh/volcano/releases/tag/v1.11.2
- https://github.com/volcano-sh/volcano/releases/tag/v1.12.0-alpha.2
- https://github.com/volcano-sh/volcano/releases/tag/v1.9.1
- https://pkg.go.dev/vuln/GO-2025-3656
