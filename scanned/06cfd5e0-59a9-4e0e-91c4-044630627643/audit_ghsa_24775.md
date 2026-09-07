# [M] Node Connect Reflected Cross-Site Scripting in Sencha Labs Connect middleware

## Summary
Severity: Medium
Advisory: GHSA-6w62-83g6-rfhj
CVE: CVE-2013-7371
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-6w62-83g6-rfhj
Type: github-advisory

## Affected
- npm: `connect` — affected >=0 <2.8.2

## Details
node-connect before 2.8.2 has cross site scripting in Sencha Labs Connect middleware (vulnerability due to incomplete fix for CVE-2013-7370)

### Overview
Connect is a stack of middleware that is executed in order in each request.

The "methodOverride" middleware allows the http post to override the method of the request with the value of the "_method" post key or with the header "x-http-method-override".

Because the user post input was not checked, req.method could contain any kind of value. Because the req.method did not match any common method VERB, connect answered with a 404 page containing the "Cannot `[method]` `[url]`" content. The method was not properly encoded for output in the browser.


### Example:
```
~ curl "localhost:3000" -d "_method=<script src=http://nodesecurity.io/xss.js></script>"
Cannot <SCRIPT SRC=HTTP://NODESECURITY.IO/XSS.JS></SCRIPT> /
```

### Recommendation

Update to the newest version of Connect or disable methodOverride. It is not possible to avoid the vulnerability if you have enabled this middleware in the top of your stack.

### Credit:
Sergio Arcos

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7371
- https://github.com/senchalabs/connect/issues/831
- https://github.com/senchalabs/connect/commit/126187c4e12162e231b87350740045e5bb06e93a
- https://github.com/senchalabs/connect/commit/277e5aad6a95d00f55571a9a0e11f2fa190d8135
- https://access.redhat.com/security/cve/cve-2013-7371
- https://exchange.xforce.ibmcloud.com/vulnerabilities/92710
- https://github.com/senchalabs/connect
- https://nodesecurity.io/advisories/methodOverride_Middleware_Reflected_Cross-Site_Scripting
- https://security-tracker.debian.org/tracker/CVE-2013-7371
- http://www.openwall.com/lists/oss-security/2014/04/21/2
- http://www.openwall.com/lists/oss-security/2014/05/13/1
