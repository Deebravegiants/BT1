# [M] CVE-2017-1000398

## Summary
Severity: Medium
Advisory: CVE-2017-1000398
Aliases: GHSA-h972-cwjv-2v39
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-1000398
Type: osv

## Details
The remote API in Jenkins 2.73.1 and earlier, 2.83 and earlier at /computer/(agent-name)/api showed information about tasks (typically builds) currently running on that agent. This included information about tasks that the current user otherwise has no access to, e.g. due to lack of Item/Read permission. This has been fixed, and the API now only shows information about accessible tasks.

## References
- https://jenkins.io/security/advisory/2017-10-11/
