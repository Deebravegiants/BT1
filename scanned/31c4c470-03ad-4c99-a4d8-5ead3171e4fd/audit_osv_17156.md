# [H] CVE-2020-13128

## Summary
Severity: High
Advisory: CVE-2020-13128
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-18
Source: https://osv.dev/vulnerability/CVE-2020-13128
Type: osv

## Details
An issue was discovered in Manolo GWTUpload 1.0.3. server/UploadServlet.java (the servlet for handling file upload) accepts a delay parameter that causes a thread to sleep. It can be abused to cause all of a server's threads to sleep, leading to denial of service.

## References
- https://github.com/manolo/gwtupload/issues/33
- https://logicaltrust.net/blog/2020/02/gwt-upload.html
