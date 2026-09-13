# [H] CVE-2022-45639

## Summary
Severity: High
Advisory: CVE-2022-45639
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-24
Source: https://osv.dev/vulnerability/CVE-2022-45639
Type: osv

## Details
OS Command injection vulnerability in sleuthkit fls tool 4.11.1 allows attackers to execute arbitrary commands via a crafted value to the m parameter. NOTE: third parties have disputed this because there is no analysis showing that the backtick command executes outside the context of the user account that entered the command line.

## References
- http://packetstormsecurity.com/files/171649/Sleuthkit-4.11.1-Command-Injection.html
- http://www.binaryworld.it/
- https://www.binaryworld.it/guidepoc.asp#CVE-2022-45639
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45639.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-45639
