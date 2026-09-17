# [M] CVE-2020-5422

## Summary
Severity: Medium
Advisory: CVE-2020-5422
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-5422
Type: osv

## Details
BOSH System Metrics Server releases prior to 0.1.0 exposed the UAA password as a flag to a process running on the BOSH director. It exposed the password to any user or process with access to the same VM (through ps or looking at process details).

## References
- https://www.cloudfoundry.org/blog/cve-2020-5422
