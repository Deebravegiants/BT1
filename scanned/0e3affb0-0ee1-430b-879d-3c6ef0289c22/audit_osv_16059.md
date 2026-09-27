# [M] CVE-2019-25210

## Summary
Severity: Medium
Advisory: CVE-2019-25210
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-03
Source: https://osv.dev/vulnerability/CVE-2019-25210
Type: osv

## Details
An issue was discovered in Cloud Native Computing Foundation (CNCF) Helm through 3.13.3. It displays values of secrets when the --dry-run flag is used. This is a security concern in some use cases, such as a --dry-run call by a CI/CD tool. NOTE: the vendor's position is that this behavior was introduced intentionally, and cannot be removed without breaking backwards compatibility (some users may be relying on these values). Also, it is not the Helm Project's responsibility if a user decides to use --dry-run within a CI/CD environment whose output is visible to unauthorized persons.

## References
- https://www.cncf.io/projects/helm/
- https://helm.sh/blog/response-cve-2019-25210/
- https://github.com/helm/helm/issues/7275
