# [H] CVE-2019-3783

## Summary
Severity: High
Advisory: CVE-2019-3783
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2019-3783
Type: osv

## Details
Cloud Foundry Stratos, versions prior to 2.3.0, deploys with a public default session store secret. A malicious user with default session store secret can brute force another user's current Stratos session, and act on behalf of that user.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3783
