# [C] CVE-2025-52921

## Summary
Severity: Critical
Advisory: CVE-2025-52921
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-52921
Type: osv

## Details
In Innoshop through 0.4.1, an authenticated attacker could exploit the File Manager functions in the admin panel to achieve code execution on the server, by uploading a crafted file and then renaming it to have a .php extension by using the Rename Function. This bypasses the initial check that uploaded files are image files. The application relies on frontend checks to restrict the administrator from changing the extension of uploaded files to .php. This restriction is easily bypassed with any proxy tool (e.g., BurpSuite). Once the attacker renames the file, and gives it the .php extension, a GET request can be used to trigger the execution of code on the server.

## References
- https://medium.com/@The_Hiker/how-i-found-multiple-cves-in-innoshop-0-4-1-12c8f84ad87f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52921.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52921
- https://github.com/innocommerce/innoshop
