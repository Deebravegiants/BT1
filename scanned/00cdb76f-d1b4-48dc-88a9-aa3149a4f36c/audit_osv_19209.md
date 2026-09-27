# [M] CVE-2020-8664

## Summary
Severity: Medium
Advisory: CVE-2020-8664
Aliases: GHSA-3x9m-pgmg-xpx8
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-03-04
Source: https://osv.dev/vulnerability/CVE-2020-8664
Type: osv

## Details
CNCF Envoy through 1.13.0 has incorrect Access Control when using SDS with Combined Validation Context. Using the same secret (e.g. trusted CA) across many resources together with the combined validation context could lead to the “static” part of the validation context to be not applied, even though it was visible in the active config dump.

## References
- https://access.redhat.com/errata/RHSA-2020:0734
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3x9m-pgmg-xpx8
- https://www.envoyproxy.io/docs/envoy/v1.13.1/intro/version_history
