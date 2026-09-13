# [H] CVE-2026-84173

## Summary
Severity: High
Advisory: CVE-2026-84173
Aliases: GHSA-rp6v-x3q5-cp2g
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-84173
Type: osv

## Details
In Eclipse Ankaios versions v0.5.1 through v1.0.1, the agent-side Control Interface authorizer incorrectly evaluates multi-segment allow rules whose first path segment is a wildcard. An authenticated workload with access restricted by such a rule can submit a CompleteStateRequest or UpdateStateRequest with an empty field mask. The request may then be incorrectly authorized as matching the scoped rule, allowing the workload to read the complete cluster state or replace state outside its authorized subtree. This may result in unauthorized disclosure or modification of other workloads and cluster configuration. Only a rule consisting solely of * is intended to authorize an empty mask.




Mitigation: Until an update containing the fix is installed, avoid multi-segment Control Interface allow-rule filter masks that begin with a wildcard, such as *.workloads.some_workload. Replace them with explicit paths such as desiredState.workloads.some_workload, where applicable. A filter mask consisting solely of * has different, intentionally unrestricted semantics and should only be used when full-state access is intended.

## References
- https://github.com/eclipse-ankaios/ankaios/releases/tag/v1.0.2
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/853
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84173.json
- https://github.com/eclipse-ankaios/ankaios/security/advisories/GHSA-rp6v-x3q5-cp2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-84173
- https://github.com/eclipse-ankaios/ankaios/pull/790
