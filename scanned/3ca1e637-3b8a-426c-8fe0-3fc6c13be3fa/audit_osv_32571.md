# [M] AutoGPT has a DoS vulnerability in MediaDurationBlock

## Summary
Severity: Medium
Advisory: CVE-2025-32437
Aliases: GHSA-rg6v-m9x9-7wf9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-32437
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.63, `MediaDurationBlock` will download and store the video in a temporary directory without deleting before all noded are done. `StepThroughItemsBlock` can be used to iterate `MediaDurationBlock` multiple times. `StepThroughItemsBlock` does not limit the number of loops. In addition, `MediaDurationBlock ` does not limit the amount of disk space consumed in the current working directory and does not delete the video after outputing the result. When a malicious user chooses to screen shot many web pages, the disk space will eventually run out, causing a DoS. Version 0.6.63 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32437.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-rg6v-m9x9-7wf9
- https://nvd.nist.gov/vuln/detail/CVE-2025-32437
