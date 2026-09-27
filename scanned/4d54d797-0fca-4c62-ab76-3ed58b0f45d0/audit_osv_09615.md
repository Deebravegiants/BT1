# [M] CVE-2017-1000399

## Summary
Severity: Medium
Advisory: CVE-2017-1000399
Aliases: GHSA-g78x-xmv8-23xp
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-1000399
Type: osv

## Details
The Jenkins 2.73.1 and earlier, 2.83 and earlier remote API at /queue/item/(ID)/api showed information about tasks in the queue (typically builds waiting to start). This included information about tasks that the current user otherwise has no access to, e.g. due to lack of Item/Read permission. This has been fixed, and the API endpoint is now only available for tasks that the current user has access to.

## References
- https://jenkins.io/security/advisory/2017-10-11/
