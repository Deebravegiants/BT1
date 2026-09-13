# [H] CVE-2018-11040

## Summary
Severity: High
Advisory: CVE-2018-11040
Aliases: GHSA-f26x-pr96-vw86
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-25
Source: https://osv.dev/vulnerability/CVE-2018-11040
Type: osv

## Details
Spring Framework, versions 5.0.x prior to 5.0.7 and 4.3.x prior to 4.3.18 and older unsupported versions, allows web applications to enable cross-domain requests via JSONP (JSON with Padding) through AbstractJsonpResponseBodyAdvice for REST controllers and MappingJackson2JsonView for browser requests. Both are not enabled by default in Spring Framework nor Spring Boot, however, when MappingJackson2JsonView is configured in an application, JSONP support is automatically ready to use through the "jsonp" and "callback" JSONP parameters, enabling cross-domain requests.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00022.html
- https://pivotal.io/security/cve-2018-11040
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
