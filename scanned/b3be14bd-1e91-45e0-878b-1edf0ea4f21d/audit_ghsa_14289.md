# [C] Strapi plugins vulnerable to Server-Side Template Injection and Remote Code Execution in the Users-Permissions Plugin

## Summary
Severity: Critical
Advisory: GHSA-2h87-4q2w-v4hf
CVE: CVE-2023-22621
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-19
Source: https://github.com/advisories/GHSA-2h87-4q2w-v4hf
Type: github-advisory

## Affected
- npm: `@strapi/plugin-users-permissions` — affected >=0 <4.5.6
- npm: `@strapi/plugin-email` — affected >=0 <4.5.6

## Details
### Summary

Strapi through 4.5.5 allows authenticated Server-Side Template Injection (SSTI) that can be exploited to execute arbitrary code on the server.

### Details

Strapi through 4.5.5 allows authenticated Server-Side Template Injection (SSTI) that can be exploited to execute arbitrary code on the server. A remote attacker with access to the Strapi admin panel can inject a crafted payload that executes code on the server into an email template that bypasses the validation checks that should prevent code execution.

### IoC

Using just the request log files, the only IoC to search for is a `PUT` request to URL path `/users-permissions/email-templates`. This IoC only indicates that a Strapi email template was modified on your server and by itself does not indicate if your Strapi server has been compromised. If this IoC is detected, you will need to manually review your email templates on your Strapi server and backups of your database to see if any of the templates contain a `lodash` template delimiter (eg. `<%STUFF HERE%>`) that contains suspicious JavaScript code. Generally speaking these templates should look like the following, you may have minor adjustments but any unrecognized code should be considered suspicious.

Reset Password Template:

```html
<p>We heard that you lost your password. Sorry about that!</p>

<p>But don’t worry! You can use the following link to reset your password:</p>
<p><%= URL %>?code=<%= TOKEN %></p>

<p>Thanks.</p>
```

Email Confirmation Template:

```html
<p>Thank you for registering!</p>

<p>You have to confirm your email address. Please click on the link below.</p>

<p><%= URL %>?confirmation=<%= CODE %></p>

<p>Thanks.</p>
```

Specifically you should look for odd code contained within the `<%STUFF HERE%>` blocks as this is what is used to bypass the lodash templating system. If you find any code that is not a variable name, or a variable name that is not defined in the template you are most likely impacted and should take immediate steps to confirm there are no malicious applications running on your servers.

### Impact

All users on Strapi below 4.5.6 with access to the admin panel and the ability to modify the email templates

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-2h87-4q2w-v4hf
- https://nvd.nist.gov/vuln/detail/CVE-2023-22621
- https://github.com/strapi/strapi/pull/15385
- https://github.com/strapi/strapi/commit/921d30961d6ba96cc098f2aea197350a49f990bd
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases
- https://github.com/strapi/strapi/releases/tag/v4.5.6
- https://strapi.io/blog/security-disclosure-of-vulnerabilities-cve
- https://www.ghostccamm.com/blog/multi_strapi_vulns
