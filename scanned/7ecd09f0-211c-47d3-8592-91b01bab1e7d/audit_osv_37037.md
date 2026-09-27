# [M] NetExec vulnerable to arbitrary file write via path traversal in spider_plus module

## Summary
Severity: Medium
Advisory: CVE-2026-27884
Aliases: GHSA-fccr-6qm2-7h27
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27884
Type: osv

## Details
NetExec is a network execution tool. Prior to version 1.5.1, the module spider_plus improperly creates the output file and folder path when saving files from SMB shares. It does not take into account that it is possible for Linux SMB shares to have path traversal characters such as `../` in them. An attacker can craft a filename in an SMB share that includes these characters, which when spider_plus crawls and downloads, can write or overwrite arbitrary files. The issue is patched in v1.5.1. As a workaround, do not run spider_plus with DOWNLOAD=true against targets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27884.json
- https://github.com/Pennyw0rth/NetExec/security/advisories/GHSA-fccr-6qm2-7h27
- https://nvd.nist.gov/vuln/detail/CVE-2026-27884
- https://github.com/Pennyw0rth/NetExec/issues/1120
- https://github.com/Pennyw0rth/NetExec/commit/7d027f2774d0520b322d60f9c99b9ab3edb4035e
- https://github.com/Pennyw0rth/NetExec/pull/1121
