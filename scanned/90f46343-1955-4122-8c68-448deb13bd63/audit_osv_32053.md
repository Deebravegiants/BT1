# [H] CVAT allows remote code execution via tracker Nuclio functions

## Summary
Severity: High
Advisory: CVE-2025-23045
Aliases: GHSA-wq36-mxf8-hv62
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2025-01-28
Source: https://osv.dev/vulnerability/CVE-2025-23045
Type: osv

## Details
Computer Vision Annotation Tool (CVAT) is an interactive video and image annotation tool for computer vision. An attacker with an account on an affected CVAT instance is able to run arbitrary code in the context of the Nuclio function container. This vulnerability affects CVAT deployments that run any of the serverless functions of type tracker from the CVAT Git repository, namely TransT and SiamMask. Deployments with custom functions of type tracker may also be affected, depending on how they handle state serialization. If a function uses an unsafe serialization library such as pickle or jsonpickle, it's likely to be vulnerable. Upgrade to CVAT 2.26.0 or later. If you are unable to upgrade, shut down any instances of the TransT or SiamMask functions you're running.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23045.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-wq36-mxf8-hv62
- https://nvd.nist.gov/vuln/detail/CVE-2025-23045
- https://github.com/cvat-ai/cvat/commit/563e1dfde64b15fa042b23f9d09cd854b35f0366
