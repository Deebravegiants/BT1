# [C] CVE-2021-35209

## Summary
Severity: Critical
Advisory: CVE-2021-35209
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-02
Source: https://osv.dev/vulnerability/CVE-2021-35209
Type: osv

## Details
An issue was discovered in ProxyServlet.java in the /proxy servlet in Zimbra Collaboration Suite 8.8 before 8.8.15 Patch 23 and 9.x before 9.0.0 Patch 16. The value of the X-Host header overwrites the value of the Host header in proxied requests. The value of X-Host header is not checked against the whitelist of hosts Zimbra is allowed to proxy to (the zimbraProxyAllowedDomains setting).

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/8.8.15/P23
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P16
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://blog.sonarsource.com/zimbra-webmail-compromise-via-email
