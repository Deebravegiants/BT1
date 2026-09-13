# [M] AutoGPT has a DoS vulnerability in AddAudioToVideoBlock

## Summary
Severity: Medium
Advisory: CVE-2025-32436
Aliases: GHSA-g26x-xwc5-7p44
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-32436
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.63, `AddAudioToVideoBlock` will download and store the video and audio in a temporary directory without deleting before all noded are done. `StepThroughItemsBlock` can be used to iterate `MediaDurationBlock` multiple times. `StepThroughItemsBlock` does not limit the number of loops. In addition, `AddAudioToVideoBlock` does not limit the amount of disk space consumed in the current working directory and does not delete the video after outputing the result. When a malicious user chooses to screen shot many web pages, the disk space will eventually run out, causing a DoS. Version 0.6.63 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32436.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-g26x-xwc5-7p44
- https://nvd.nist.gov/vuln/detail/CVE-2025-32436
