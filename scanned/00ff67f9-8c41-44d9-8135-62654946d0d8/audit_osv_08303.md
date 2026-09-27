# [M] CVE-2016-2169

## Summary
Severity: Medium
Advisory: CVE-2016-2169
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-04-18
Source: https://osv.dev/vulnerability/CVE-2016-2169
Type: osv

## Details
Cloud Foundry Cloud Controller, capi-release versions prior to 1.0.0 and cf-release versions prior to v237, contain a business logic flaw. An application developer may create an application with a route that conflicts with a platform service route and receive traffic intended for the service.

## References
- https://github.com/cloudfoundry/cloud_controller_ng/issues/568
