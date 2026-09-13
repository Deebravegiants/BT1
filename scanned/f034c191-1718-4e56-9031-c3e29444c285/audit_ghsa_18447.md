# [H] HAX CMS NodeJS Application Has Improper Error Handling That Leads to Denial of Service

## Summary
Severity: High
Advisory: GHSA-pjj3-j5j6-qj27
CVE: CVE-2025-54134
CWE: CWE-20, CWE-248, CWE-703
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-pjj3-j5j6-qj27
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.9

## Details
### Summary
The HAX CMS NodeJS application crashes when an authenticated attacker provides an API request lacking required URL parameters. This vulnerability affects the `listFiles` and `saveFiles` endpoints.

### Details
This vulnerability exists because the application does not properly handle exceptions which occur as a result of changes to user-modifiable URL parameters.

#### Affected Resources
• [listFiles.js:22](https://github.com/haxtheweb/haxcms-nodejs/blob/main/src/routes/listFiles.js#L22) listFiles()
• [saveFile.js:52](https://github.com/haxtheweb/haxcms-nodejs/blob/main/src/routes/saveFile.js#L52) saveFile()
• system/api/listFiles
• system/api/saveFile

### PoC
1. Targeting an instance of instance of [HAX CMS NodeJS](https://github.com/haxtheweb/haxcms-nodejs), send a request without parameters to `listFiles` or `saveFiles`. The following screenshot shows the request in Burp Suite.
![listfilesrequest](https://github.com/user-attachments/assets/477ea4e0-5707-4948-b53c-7f042a0475fb)

2. The server will crash with `ERR_INVALID_ARG_TYPE`.
![listfilescrash](https://github.com/user-attachments/assets/85424c12-1619-41d3-9bf5-9e029cdaa8c1)

### Impact
An authenticated attacker can deny access to the HAX CMS NodeJS application by crashing the backend server. This prevents all users from accessing the backend system. If the backend system is hosting websites, those websites will be unavailable.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-pjj3-j5j6-qj27
- https://nvd.nist.gov/vuln/detail/CVE-2025-54134
- https://github.com/haxtheweb/haxcms-nodejs/commit/e9773d1996233f9bafb06832b8220ec2a98bab34
- https://github.com/haxtheweb/haxcms-nodejs
- https://github.com/haxtheweb/haxcms-nodejs/blob/main/src/routes/listFiles.js#L22
- https://github.com/haxtheweb/haxcms-nodejs/blob/main/src/routes/saveFile.js#L52
