# [H] Misconfigured Internal Proxy in runtimes-inventory-rhel8-operator Grants Standard Users Full Cluster Administrator Access

## Summary
Severity: High
Advisory: GHSA-cc8c-28gj-px38
CVE: CVE-2025-11393
CWE: CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-cc8c-28gj-px38
Type: github-advisory

## Affected
- Go: `github.com/RedHatInsights/runtimes-inventory-operator` — affected >=0

## Details
A flaw was found in runtimes-inventory-rhel8-operator. An internal proxy component is incorrectly configured. Because of this flaw, the proxy attaches the cluster's main administrative credentials to any command it receives, instead of only the specific reports it is supposed to handle.

This allows a standard user within the cluster to send unauthorized commands to the management platform, effectively acting with the full permissions of the cluster administrator. This could lead to unauthorized changes to the cluster's configuration or status on the Red Hat platform.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11393
- https://access.redhat.com/errata/RHSA-2025:23236
- https://access.redhat.com/security/cve/CVE-2025-11393
- https://bugzilla.redhat.com/show_bug.cgi?id=2402032
- https://github.com/RedHatInsights/runtimes-inventory-operator
