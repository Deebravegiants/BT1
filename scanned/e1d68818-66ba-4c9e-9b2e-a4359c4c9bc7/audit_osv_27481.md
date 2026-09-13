# [M] GoRouter Denial of Service Attack

## Summary
Severity: Medium
Advisory: CVE-2024-22279
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-10
Source: https://osv.dev/vulnerability/CVE-2024-22279
Type: osv

## Details
Improper handling of requests in Routing Release > v0.273.0 and <= v0.297.0 allows an unauthenticated attacker to degrade
 the service availability of the Cloud Foundry deployment if performed at scale.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22279.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22279
- https://www.cloudfoundry.org/blog/cve-2024-22279-gorouter-denial-of-service-attack/
