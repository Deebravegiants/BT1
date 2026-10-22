# [M] CVE-2017-14389

## Summary
Severity: Medium
Advisory: CVE-2017-14389
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-11-28
Source: https://osv.dev/vulnerability/CVE-2017-14389
Type: osv

## Details
An issue was discovered in Cloud Foundry Foundation capi-release (all versions prior to 1.45.0), cf-release (all versions prior to v280), and cf-deployment (all versions prior to v1.0.0). The Cloud Controller does not prevent space developers from creating subdomains to an already existing route that belongs to a different user in a different org and space, aka an "Application Subdomain Takeover."

## References
- https://www.cloudfoundry.org/cve-2017-14389/
