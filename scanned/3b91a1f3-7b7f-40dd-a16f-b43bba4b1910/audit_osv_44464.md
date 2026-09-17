# [C] UnoPim File Upload RCE via TinyMCE Image Upload Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-82524
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-82524
Type: osv

## Details
UnoPim before 2.1.5 contains an authenticated file upload vulnerability that allows authenticated administrators to upload arbitrary PHP files through the TinyMCE image upload endpoint due to missing file extension and MIME type validation. Attackers can upload a PHP web shell to the public storage disk and execute arbitrary operating system commands on the server by accessing the uploaded file at the URL returned in the server response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82524.json
- https://github.com/unopim/unopim/releases/tag/v2.1.5
- https://nvd.nist.gov/vuln/detail/CVE-2026-82524
- https://www.vulncheck.com/advisories/unopim-file-upload-rce-via-tinymce-image-upload-endpoint
- https://github.com/unopim/unopim/commit/675dfb5155a87f94c5ac861545a31b8f6ea44f5b
- https://github.com/unopim/unopim
- https://ashutosh-jena.in/blog/remote-code-execution-rce-via-unrestricted-file-upload-in-unopim-v214
