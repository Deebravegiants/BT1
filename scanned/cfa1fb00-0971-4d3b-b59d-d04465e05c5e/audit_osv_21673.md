# [H] CVE-2021-45101

## Summary
Severity: High
Advisory: CVE-2021-45101
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-45101
Type: osv

## Details
An issue was discovered in HTCondor before 8.8.15, 9.0.x before 9.0.4, and 9.1.x before 9.1.2. Using standard command-line tools, a user with only READ access to an HTCondor SchedD or Collector daemon can discover secrets that could allow them to control other users' jobs and/or read their data.

## References
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2021-0003/
