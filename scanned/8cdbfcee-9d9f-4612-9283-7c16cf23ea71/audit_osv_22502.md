# [H] Insufficient content-type validation for uploaded files in open-forms

## Summary
Severity: High
Advisory: CVE-2022-31041
Aliases: GHSA-h85r-xv4w-cg8g
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2022-06-13
Source: https://osv.dev/vulnerability/CVE-2022-31041
Type: osv

## Details
Open Forms is an application for creating and publishing smart forms. Open Forms supports file uploads as one of the form field types. These fields can be configured to allow only certain file extensions to be uploaded by end users (e.g. only PDF / Excel / ...). The input validation of uploaded files is insufficient in versions prior to 1.0.9 and 1.1.1. Users could alter or strip file extensions to bypass this validation. This results in files being uploaded to the server that are of a different file type than indicated by the file name extension. These files may be downloaded (manually or automatically) by staff and/or other applications for further processing. Malicious files can therefore find their way into internal/trusted networks. Versions 1.0.9 and 1.1.1 contain patches for this issue. As a workaround, an API gateway or intrusion detection solution in front of open-forms may be able to scan for and block malicious content before it reaches the Open Forms application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31041.json
- https://github.com/open-formulieren/open-forms/security/advisories/GHSA-h85r-xv4w-cg8g
- https://nvd.nist.gov/vuln/detail/CVE-2022-31041
- https://github.com/open-formulieren/open-forms/commit/0978a29e821a7228c5d46c0527c3e925eb91b071
