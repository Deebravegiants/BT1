# [H] Piccolo Admin's raw SVG loading may lead to complete data compromise from admin page

## Summary
Severity: High
Advisory: GHSA-pmww-v6c9-7p83
CVE: CVE-2024-30248
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-01
Source: https://github.com/advisories/GHSA-pmww-v6c9-7p83
Type: github-advisory

## Affected
- PyPI: `piccolo-admin` — affected >=1.2.0 <1.3.2

## Details
### Summary

Piccolo's admin panel provides the ability to upload media files and view them within the admin panel. If SVG is an allowed file type for upload; the default; an attacker can upload an SVG which when loaded under certain contexts allows for arbitrary access to the admin page. 

This access allows the following actions for example:
- The ability for an attacker to gain access to all data stored within the admin page
- The ability for an attacker to make any action within the admin page such as creating, modifying or deleting table records

As the SVG is executed from the context of an authenticated admin session, any actions they may be able to make can be made by the attacker. 

*N.b. The relevant session cookies are inaccessible from JavaScript due to httponly being set so all exploits must be present within the SVG file*

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

Currently, this requires the ability for a user to have access to an administrators account in order to upload the malicious file for simplicity sake. I can however imagine situations where general end users have the ability to upload files which can later be managed via the admin page. 

See the following repository: [Piccolo XSS](https://github.com/Skelmis/piccolo_xss)

1. Clone the repo
2. Run all migrations & create an admin user
3. Run `app.py` as a FastAPI application
4. Login to the admin page
5. Create a new task and upload the following file to see basic execution: `payloads/basic_xss.svg`
6. Click the SVG to view it inline 
7. Click "Open image in new tab"
8. Observe the XSS triggering


*Fig 1: An example XSS payload executing*
![Example XSS](https://user-images.githubusercontent.com/47520067/300751626-ba09c524-ffd8-43b8-963e-9bc6803e3388.png)


##### Extended PoC

This repo also includes an extended PoC which sends the `Task` table to an attacker controlled server.

1. Run `exhil_server.py` as a FastAPI application
2. Upload the following payload: `payloads/exhil.svg`
3. Open the SVG in a new tab and observe the data being sent to the attacker controlled server

*Fig 2: An example screenshot from the attacker controlled server showing incoming data*
![Example data sent to attacker server](https://user-images.githubusercontent.com/47520067/300746553-9895217b-b509-4e03-b3bc-9ae730450e32.png)

Further, the repo includes a list of routes the admin panel exposes which could be used to automate table discovery and compromise in a more sophisticated PoC.

### Impact
_What kind of vulnerability is it? Who is impacted?_

All applications with the following conditions present are affected:
- An enabled admin panel
- A model which features media upload that allows for SVG files

Further, if the site is behind a proxy of sorts it must not set the relevant security headers.

### Further thoughts

While this issue has been raised against the `piccolo_admin` repository, it technically exists for all file uploads within a piccolo website if an end developer chooses to include the ability to view SVG files inline within their application. Further thought should likely be given to either or both of the following:
- Ensuring the documentation for media handling includes some form of warning/recommendation relating to this. Ideally I think it should just provide an example of a code fix and link to security headers to test their own application
- Modifying the Piccolo template generation to include the relevant security headers by default. These include things such as xss protection and a content security policy. [This](https://securityheaders.com/) site is a great resource for testing the security headers set on a website

Given the need to allow end developers the freedom to allow for SVG upload, removing the ability to upload them entirely is likely out of the picture. 

This could also be resolved by making attempts to view attachments in a new tab set the relevant content-disposition header and force the browser to download the file instead of rendering it inline of the website.

What are your thoughts on the approach to take to mitigate this?

## References
- https://github.com/piccolo-orm/piccolo_admin/security/advisories/GHSA-pmww-v6c9-7p83
- https://nvd.nist.gov/vuln/detail/CVE-2024-30248
- https://github.com/piccolo-orm/piccolo_admin/commit/c419575c2467959d906154084d305648eb2b8faf
- https://github.com/piccolo-orm/piccolo_admin
