# [M] Computer Vision Annotation Tool (CVAT) is missing authorization for endpoints related to webhook deliveries

## Summary
Severity: Medium
Advisory: CVE-2024-45393
Aliases: GHSA-p3c9-m7jr-jxxj
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/CVE-2024-45393
Type: osv

## Details
Computer Vision Annotation Tool (CVAT) is an interactive video and image annotation tool for computer vision. An attacker with a CVAT account can access webhook delivery information for any webhook registered on the CVAT instance, including that of other users. For each delivery, this contains information about the event that caused the delivery, typically including full details about the object on which an action was performed (such as the task for an "update:task" event), and the user who performed the action. In addition, the attacker can redeliver any past delivery of any webhook, and trigger a ping event for any webhook. Upgrade to CVAT 2.18.0 or any later version.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45393.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-p3c9-m7jr-jxxj
- https://nvd.nist.gov/vuln/detail/CVE-2024-45393
- https://github.com/cvat-ai/cvat/commit/0fafb797fdf022fb83ce81c6405ba19b583a236f
