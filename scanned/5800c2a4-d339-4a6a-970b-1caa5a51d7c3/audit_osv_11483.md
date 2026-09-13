# [M] CVE-2017-8034

## Summary
Severity: Medium
Advisory: CVE-2017-8034
CVSS: 6.6 (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-8034
Type: osv

## Details
The Cloud Controller and Router in Cloud Foundry (CAPI-release capi versions prior to v1.32.0, Routing-release versions prior to v0.159.0, CF-release versions prior to v267) do not validate the issuer on JSON Web Tokens (JWTs) from UAA. With certain multi-zone UAA configurations, zone administrators are able to escalate their privileges.

## References
- https://www.cloudfoundry.org/cve-2017-8034/
