# [M] Cryostat: authentication bypass if network policies are disabled

## Summary
Severity: Medium
Advisory: CVE-2025-8415
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-08-20
Source: https://osv.dev/vulnerability/CVE-2025-8415
Type: osv

## Details
A vulnerability was found in the Cryostat HTTP API. Cryostat's HTTP API binds to all network interfaces, allowing possible external visibility and access to the API port if Network Policies are disabled, allowing an unauthenticated, malicious attacker to jeopardize the environment.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://github.com/cryostatio/cryostat/releases/tag/v4.0.2
- https://access.redhat.com/errata/RHSA-2025:14919
- https://access.redhat.com/security/cve/CVE-2025-8415
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8415.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-8415
- https://bugzilla.redhat.com/show_bug.cgi?id=2385773
- https://github.com/cryostatio/cryostat/pull/1001
- https://github.com/cryostatio/cryostat
