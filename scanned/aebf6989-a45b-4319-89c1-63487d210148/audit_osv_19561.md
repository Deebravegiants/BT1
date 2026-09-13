# [M] CVE-2021-22100

## Summary
Severity: Medium
Advisory: CVE-2021-22100
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-22100
Type: osv

## Details
In cloud foundry CAPI versions prior to 1.122, a denial-of-service attack in which a developer can push a service broker that (accidentally or maliciously) causes CC instances to timeout and fail is possible. An attacker can leverage this vulnerability to cause an inability for anyone to push or manage apps.

## References
- https://www.cloudfoundry.org/blog/cve-2021-22100-cloud-controller-is-vulnerable-to-denial-of-service-due-to-misbehaving-service-brokers/
