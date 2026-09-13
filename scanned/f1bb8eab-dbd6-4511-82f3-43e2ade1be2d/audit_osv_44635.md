# [M] CVE-2026-85201

## Summary
Severity: Medium
Advisory: CVE-2026-85201
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-85201
Type: osv

## Details
In Eclipse Ankaios versions 0.1.0 through 1.0.1, the agent does not limit the length declared by a workload in a length-delimited protobuf message received through the Control Interface FIFO. A workload granted Control Interface access can specify an excessive message length, causing an unbounded memory allocation that may abort the Ankaios agent process. This results in loss of orchestration services for workloads managed by the affected agent.

## References
- https://github.com/eclipse-ankaios/ankaios/releases/tag/v1.0.2
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/900
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85201.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85201
- https://github.com/eclipse-ankaios/ankaios/pull/791
