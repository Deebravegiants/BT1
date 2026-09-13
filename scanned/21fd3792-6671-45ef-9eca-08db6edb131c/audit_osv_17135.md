# [M] CVE-2020-12803

## Summary
Severity: Medium
Advisory: CVE-2020-12803
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-12803
Type: osv

## Details
ODF documents can contain forms to be filled out by the user. Similar to HTML forms, the contained form data can be submitted to a URI, for example, to an external web server. To create submittable forms, ODF implements the XForms W3C standard, which allows data to be submitted without the need for macros or other active scripting Prior to version 6.4.4 LibreOffice allowed forms to be submitted to any URI, including file: URIs, enabling form submissions to overwrite local files. User-interaction is required to submit the form, but to avoid the possibility of malicious documents engineered to maximize the possibility of inadvertent user submission this feature has now been limited to http[s] URIs, removing the possibility to overwrite local files. This issue affects: The Document Foundation LibreOffice versions prior to 6.4.4.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00058.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PQIBAKXD7VO5IGBD7ZMH3GGBNR5R2IOA/
- https://www.libreoffice.org/about-us/security/advisories/CVE-2020-12803
