# [C] CVE-2021-25311

## Summary
Severity: Critical
Advisory: CVE-2021-25311
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2021-25311
Type: osv

## Details
condor_credd in HTCondor before 8.9.11 allows Directory Traversal outside the SEC_CREDENTIAL_DIRECTORY_OAUTH directory, as demonstrated by creating a file under /etc that will later be executed by root.

## References
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2021-0002.html
