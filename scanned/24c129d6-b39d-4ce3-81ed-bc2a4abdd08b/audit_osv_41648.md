# [M] CVE-2026-62927

## Summary
Severity: Medium
Advisory: CVE-2026-62927
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-62927
Type: osv

## Details
In Eclipse Milo versions 1.0.0 through 1.1.4, the Call service dispatches the original mixed batch to address-space handlers after calculating authorization, allowing an anonymous or otherwise low-privileged client to execute a denied method by batching it with an allowed method.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/178
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62927.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62927
- https://github.com/eclipse-milo/milo/commit/59b50bed094de0d18a130a48f3527254dc76105d
