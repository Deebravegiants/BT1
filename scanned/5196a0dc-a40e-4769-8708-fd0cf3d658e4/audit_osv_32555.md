# [M] AutoGPT has a DoS vulnerability in LoopVideoBlock

## Summary
Severity: Medium
Advisory: CVE-2025-32392
Aliases: GHSA-267x-8jx3-gg6w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-32392
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.63, AutoGPT's LoopVideoBLock allows users to input a video file and process the video, such as looping it 5 times or extending the time, and finally writing it to disk. However, there is no limit on the resources that can be allocated during execution. For example, the number of loops is user-controllable and unlimited. When a malicious attacker loops too many times, the generated video is too large, and after writing it to disk, the disk space is exhausted, eventually causing DoS. Version 0.6.63 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32392.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-267x-8jx3-gg6w
- https://nvd.nist.gov/vuln/detail/CVE-2025-32392
