# [C] OpenAM vulnerable to user impersonation using SAMLv1.x SSO process

## Summary
Severity: Critical
Advisory: GHSA-4mh8-9wq6-rjxg
CVE: CVE-2023-37471
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-4mh8-9wq6-rjxg
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-federation-library` — affected >=0 <14.7.3

## Details
### Impact
OpenAM up to version 14.7.2 does not properly validate the signature of SAML responses received as part of the SAMLv1.x Single Sign-On process. Attackers can use this fact to impersonate any OpenAM user, including the administrator, by sending a specially crafted SAML response to the SAMLPOSTProfileServlet servlet.

### Patches
This problem has been patched in  OpenAM 14.7.3-SNAPSHOT and later

### Workarounds
One should comment servlet `SAMLPOSTProfileServlet` in web.xml or disable SAML in OpenAM
```xml
<servlet>
    <description>SAMLPOSTProfileServlet</description>
    <servlet-name>SAMLPOSTProfileServlet</servlet-name>
    <servlet-class>com.sun.identity.saml.servlet.SAMLPOSTProfileServlet</servlet-class>
</servlet>
...
<servlet-mapping>
    <servlet-name>SAMLSOAPReceiver</servlet-name>
    <url-pattern>/SAMLSOAPReceiver</url-pattern>
</servlet-mapping>
```

### References
#624

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-4mh8-9wq6-rjxg
- https://nvd.nist.gov/vuln/detail/CVE-2023-37471
- https://github.com/OpenIdentityPlatform/OpenAM/pull/624
- https://github.com/OpenIdentityPlatform/OpenAM/commit/7c18543d126e8a567b83bb4535631825aaa9d742
- https://github.com/OpenIdentityPlatform/OpenAM
