# [M] CVE-2017-1000094

## Summary
Severity: Medium
Advisory: CVE-2017-1000094
Aliases: GHSA-69cj-g7mw-mh72
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000094
Type: osv

## Details
Docker Commons Plugin provides a list of applicable credential IDs to allow users configuring a job to select the one they'd like to use to authenticate with a Docker Registry. This functionality did not check permissions, allowing any user with Overall/Read permission to get a list of valid credentials IDs. Those could be used as part of an attack to capture the credentials using another vulnerability.

## References
- https://jenkins.io/security/advisory/2017-07-10/
