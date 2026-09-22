# [C] Grails Spring Security Core plugin vulnerable to privilege escalation

## Summary
Severity: Critical
Advisory: CVE-2022-41923
Aliases: GHSA-frqg-vvxg-jqqh
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-41923
Type: osv

## Details
Grails Spring Security Core plugin is vulnerable to privilege escalation. The vulnerability allows an attacker access to one endpoint (i.e. the targeted endpoint) using the authorization requirements of a different endpoint (i.e. the donor endpoint). In some Grails framework applications, access to the targeted endpoint will be granted based on meeting the authorization requirements of the donor endpoint, which can result in a privilege escalation attack. This vulnerability has been patched in grails-spring-security-core versions 3.3.2, 4.0.5 and 5.1.1. Impacted Applications: Grails Spring Security Core plugin versions: 1.x 2.x >=3.0.0 <3.3.2 >=4.0.0 <4.0.5 >=5.0.0 <5.1.1 We strongly suggest that all Grails framework applications using the Grails Spring Security Core plugin be updated to a patched release of the plugin. Workarounds: Users should create a subclass extending one of the following classes from the `grails.plugin.springsecurity.web.access.intercept` package, depending on their security configuration: * `AnnotationFilterInvocationDefinition` * `InterceptUrlMapFilterInvocationDefinition` * `RequestmapFilterInvocationDefinition` In each case, the subclass should override the `calculateUri` method like so: ``` @Override protected String calculateUri(HttpServletRequest request) { UrlPathHelper.defaultInstance.getRequestUri(request) } ``` This should be considered a temporary measure, as the patched versions of grails-spring-security-core deprecates the `calculateUri` method. Once upgraded to a patched version of the plugin, this workaround is no longer needed. The workaround is especially important for version 2.x, as no patch is available version 2.x of the GSSC plugin.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41923.json
- https://github.com/grails/grails-spring-security-core/security/advisories/GHSA-frqg-vvxg-jqqh
- https://nvd.nist.gov/vuln/detail/CVE-2022-41923
- https://github.com/grails/GSSC-CVE-2022-41923
- https://grails.org/blog/2022-11-22-ss-plugin-auth-cve.html
