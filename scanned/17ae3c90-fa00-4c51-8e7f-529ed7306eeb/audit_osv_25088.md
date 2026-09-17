# [M] Malicious HTTP requests could close arbitrary opening file descriptors in cloud-hypervisor

## Summary
Severity: Medium
Advisory: CVE-2023-30612
Aliases: GHSA-g6mw-f26h-4jgp
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-30612
Type: osv

## Details
Cloud hypervisor is a Virtual Machine Monitor for Cloud workloads. This vulnerability allows users to close arbitrary open file descriptors in the Cloud Hypervisor process via sending malicious HTTP request through the HTTP API socket. As a result, the Cloud Hypervisor process can be easily crashed, causing Deny-of-Service (DoS). This can also be a potential Use-After-Free (UAF) vulnerability. Users require to have the write access to the API socket file to trigger this vulnerability.  Impacted versions of Cloud Hypervisor include upstream main branch, v31.0, and v30.0. The vulnerability was initially detected by our `http_api_fuzzer` via oss-fuzz. This issue has been addressed in versions 30.1 and 31.1. Users unable to upgrade may mitigate this issue by ensuring the write access to the API socket file is granted to trusted users only.

## References
- https://oss-fuzz.com/testcase-detail/5260873569796096
- https://oss-fuzz.com/testcase-detail/5426283514560512
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30612.json
- https://github.com/cloud-hypervisor/cloud-hypervisor/security/advisories/GHSA-g6mw-f26h-4jgp
- https://nvd.nist.gov/vuln/detail/CVE-2023-30612
- https://github.com/cloud-hypervisor/cloud-hypervisor/pull/5350
- https://github.com/cloud-hypervisor/cloud-hypervisor/pull/5373
