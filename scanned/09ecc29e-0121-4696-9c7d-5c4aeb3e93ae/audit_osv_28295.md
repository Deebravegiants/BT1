# [C] Remote Code Execution in mintplex-labs/anything-llm

## Summary
Severity: Critical
Advisory: CVE-2024-3104
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-3104
Type: osv

## Details
A remote code execution vulnerability exists in mintplex-labs/anything-llm due to improper handling of environment variables. Attackers can exploit this vulnerability by injecting arbitrary environment variables via the `POST /api/system/update-env` endpoint, which allows for the execution of arbitrary code on the host running anything-llm. The vulnerability is present in the latest version of anything-llm, with the latest commit identified as fde905aac1812b84066ff72e5f2f90b56d4c3a59. This issue has been fixed in version 1.0.0. Successful exploitation could lead to code execution on the host, enabling attackers to read and modify data accessible to the user running the service, potentially leading to a denial of service.

## References
- https://huntr.com/bounties/4f2fcb45-5828-4bec-985a-9d3a0ee00462
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3104.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3104
- https://github.com/mintplex-labs/anything-llm/commit/bfedfebfab032e6f4d5a369c8a2f947c5d0c5286
