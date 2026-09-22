# [M] CVE-2023-32750

## Summary
Severity: Medium
Advisory: CVE-2023-32750
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-32750
Type: osv

## Details
Pydio Cells through 4.1.2 allows SSRF. For longer running processes, Pydio Cells allows for the creation of jobs, which are run in the background. The job "remote-download" can be used to cause the backend to send a HTTP GET request to a specified URL and save the response to a new file. The response file is then available in a user-specified folder in Pydio Cells.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32750.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32750
- https://www.redteam-pentesting.de/advisories/rt-sa-2023-005/
- https://www.redteam-pentesting.de/en/advisories/-advisories-publicised-vulnerability-analyses
