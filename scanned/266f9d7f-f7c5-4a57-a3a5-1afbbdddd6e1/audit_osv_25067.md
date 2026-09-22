# [H] CVE-2023-30513

## Summary
Severity: High
Advisory: CVE-2023-30513
Aliases: GHSA-v5hq-cqqr-6w4g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-30513
Type: osv

## Details
Jenkins Kubernetes Plugin 3909.v1f2c633e8590 and earlier does not properly mask (i.e., replace with asterisks) credentials in the build log when push mode for durable task logging is enabled.

## References
- http://www.openwall.com/lists/oss-security/2023/04/13/3
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-3075
