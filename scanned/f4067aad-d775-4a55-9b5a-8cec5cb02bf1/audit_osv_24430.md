# [M] CVE-2023-20882

## Summary
Severity: Medium
Advisory: CVE-2023-20882
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-20882
Type: osv

## Details
In Cloud foundry routing release versions from 0.262.0 and prior to 0.266.0,a bug in the gorouter process can lead to a denial of service of applications hosted on Cloud Foundry. Under the right circumstances, when client connections are closed prematurely, gorouter marks the currently selected backend as failed and removes it from the routing pool.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/20xxx/CVE-2023-20882.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-20882
- https://www.cloudfoundry.org/blog/cve-2023-20882-gorouter-pruning-via-client-disconnect-resulting-in-dos/
