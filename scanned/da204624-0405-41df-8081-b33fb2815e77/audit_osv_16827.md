# [H] CVE-2019-9900

## Summary
Severity: High
Advisory: CVE-2019-9900
Aliases: GHSA-x74r-f4mw-c32h
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2019-04-25
Source: https://osv.dev/vulnerability/CVE-2019-9900
Type: osv

## Details
When parsing HTTP/1.x header values, Envoy 1.9.0 and before does not reject embedded zero characters (NUL, ASCII 0x0). This allows remote attackers crafting header values containing embedded NUL characters to potentially bypass header matching rules, gaining access to unauthorized resources.

## References
- https://groups.google.com/forum/#%21topic/envoy-announce/VoHfnDqZiAM
- https://access.redhat.com/errata/RHSA-2019:0741
- https://www.envoyproxy.io/docs/envoy/v1.9.1/intro/version_history
- https://github.com/envoyproxy/envoy/issues/6434
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-x74r-f4mw-c32h
