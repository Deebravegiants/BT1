# [M] CVE-2019-3789

## Summary
Severity: Medium
Advisory: CVE-2019-3789
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-3789
Type: osv

## Details
Cloud Foundry Routing Release, all versions prior to 0.188.0, contains a vulnerability that can hijack the traffic to route services hosted outside the platform. A user with space developer permissions can create a private domain that shadows the external domain of the route service, and map that route to an app. When the gorouter receives traffic destined for the external route service, this traffic will instead be directed to the internal app using the shadow route.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3789
