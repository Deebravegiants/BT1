# [H] CVE-2018-1221

## Summary
Severity: High
Advisory: CVE-2018-1221
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-03-19
Source: https://osv.dev/vulnerability/CVE-2018-1221
Type: osv

## Details
In cf-deployment before 1.14.0 and routing-release before 0.172.0, the Cloud Foundry Gorouter mishandles WebSocket requests for AWS Application Load Balancers (ALBs) and some other HTTP-aware Load Balancers. A user with developer privileges could use this vulnerability to steal data or cause denial of service.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1221/
