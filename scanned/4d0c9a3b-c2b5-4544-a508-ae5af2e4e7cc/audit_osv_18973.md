# [M] CVE-2020-5400

## Summary
Severity: Medium
Advisory: CVE-2020-5400
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-5400
Type: osv

## Details
Cloud Foundry Cloud Controller (CAPI), versions prior to 1.91.0, logs properties of background jobs when they are run, which may include sensitive information such as credentials if provided to the job. A malicious user with access to those logs may gain unauthorized access to resources protected by such credentials.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5400
