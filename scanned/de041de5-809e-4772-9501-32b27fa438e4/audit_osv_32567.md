# [M] AutoGPT has a DoS vulnerability in FileStoreBlock with StepThroughItemsBlock

## Summary
Severity: Medium
Advisory: CVE-2025-32422
Aliases: GHSA-9fr4-9jj9-mhh6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-32422
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.63, `StepThroughItemsBlock` can iterate all the contents in a list and send them to `FileStoreBlock` for downloading one by one. Although `FileStoreBlock` has access time limits for downloading files, `StepThroughItemsBlock` can be used to slowly iterate and download relatively small files (e.g., 100M) multiple times. `StepThroughItemsBlock` does not limit the number of loops. In addition, `FileStoreBlock` does not limit the amount of disk space consumed in the current working directory. When a malicious user chooses to download too many videos, the disk space will eventually run out, causing a DoS. Version 0.6.63 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32422.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-9fr4-9jj9-mhh6
- https://nvd.nist.gov/vuln/detail/CVE-2025-32422
