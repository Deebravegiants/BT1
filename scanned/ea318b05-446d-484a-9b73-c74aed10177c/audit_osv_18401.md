# [C] CVE-2020-27304

## Summary
Severity: Critical
Advisory: CVE-2020-27304
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2020-27304
Type: osv

## Details
The CivetWeb web library does not validate uploaded filepaths when running on an OS other than Windows, when using the built-in HTTP form-based file upload mechanism, via the mg_handle_form_request API. Web applications that use the file upload form handler, and use parts of the user-controlled filename in the output path, are susceptible to directory traversal

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://groups.google.com/g/civetweb/c/yPBxNXdGgJQ
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://jfrog.com/blog/cve-2020-27304-rce-via-directory-traversal-in-civetweb-http-server/
