# [C] CVE-2019-18802

## Summary
Severity: Critical
Advisory: CVE-2019-18802
Aliases: GHSA-356m-vhw2-wcm4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-13
Source: https://osv.dev/vulnerability/CVE-2019-18802
Type: osv

## Details
An issue was discovered in Envoy 1.12.0. An untrusted remote client may send an HTTP header (such as Host) with whitespace after the header content. Envoy will treat "header-value " as a different string from "header-value" so for example with the Host header "example.com " one could bypass "example.com" matchers.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00034.html
- https://groups.google.com/forum/#%21forum/envoy-users
- https://github.com/envoyproxy/envoy/commits/master
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-356m-vhw2-wcm4
