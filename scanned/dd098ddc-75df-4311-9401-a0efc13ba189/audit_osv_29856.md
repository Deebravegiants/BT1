# [M] Computer Vision Annotation Tool (CVAT) access control is broken in several PATCH endpoints

## Summary
Severity: Medium
Advisory: CVE-2024-47172
Aliases: GHSA-gxhm-hg65-5gh2
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-09-30
Source: https://osv.dev/vulnerability/CVE-2024-47172
Type: osv

## Details
Computer Vision Annotation Tool (CVAT) is an interactive video and image annotation tool for computer vision. An attacker with a CVAT account may retrieve certain information about any project, task, job or membership resource on the CVAT instance. The information exposed in this way is the same as the information returned on a GET request to the resource. In addition, the attacker can also alter the default source and target storage associated with any project or task. Upgrade to CVAT 2.19.1 or any later version to fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47172.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-gxhm-hg65-5gh2
- https://nvd.nist.gov/vuln/detail/CVE-2024-47172
- https://github.com/cvat-ai/cvat/commit/59ce6ca784a0d426b2cfb8cf2850ba1d520c03f5
