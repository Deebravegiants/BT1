# [H] WesHacks code includes links to Leostop tracking spyware infested files

## Summary
Severity: High
Advisory: CVE-2024-52583
Aliases: GHSA-462m-5c66-4pmh
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-52583
Type: osv

## Details
The WesHacks GitHub repository provides the official Hackathon competition website source code for the Muweilah Wesgreen Hackathon. The page `schedule.html` before 17 November 2024 or commit 93dfb83 contains links to `Leostop`, a site that hosts a malicious injected JavaScript file that occurs when bootstrap is run as well as jquery. `Leostop` may be a tracking malware and creates 2 JavaScript files, but little else is known about it. The WesHacks website remove all references to `Leostop` as of 17 November 2024.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52583.json
- https://github.com/DefinetlyNotAI/WesHacks/security/advisories/GHSA-462m-5c66-4pmh
- https://nvd.nist.gov/vuln/detail/CVE-2024-52583
- https://github.com/DefinetlyNotAI/WesHacks/commit/93dfb83cb23a8d44e81dc12424ad8a5ea05e8f96
- https://github.com/DefinetlyNotAI/WesHacks/commit/ea5a4112d94bfe47beb74b8a1ba9b631d10f64f0
