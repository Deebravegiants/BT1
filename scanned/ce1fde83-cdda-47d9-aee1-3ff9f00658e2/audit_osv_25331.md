# [H] CVE-2023-34061 – Gorouter route pruning

## Summary
Severity: High
Advisory: CVE-2023-34061
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-34061
Type: osv

## Details
Cloud Foundry routing release versions from v0.163.0 to v0.283.0 are vulnerable to a DOS attack.  An unauthenticated attacker can use this vulnerability to force route pruning and therefore degrade the service availability of the Cloud Foundry deployment.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34061.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34061
- https://www.cloudfoundry.org/blog/cve-2023-34061-gorouter-route-pruning/
