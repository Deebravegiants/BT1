# [M] CVE-2020-5418

## Summary
Severity: Medium
Advisory: CVE-2020-5418
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/CVE-2020-5418
Type: osv

## Details
Cloud Foundry CAPI (Cloud Controller) versions prior to 1.98.0 allow authenticated users having only the "cloud_controller.read" scope, but no roles in any spaces, to list all droplets in all spaces (whereas they should see none).

## References
- https://www.cloudfoundry.org/blog/cve-2020-5418
