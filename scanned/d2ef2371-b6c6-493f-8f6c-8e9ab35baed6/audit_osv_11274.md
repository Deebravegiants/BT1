# [H] CVE-2017-7185

## Summary
Severity: High
Advisory: CVE-2017-7185
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2017-7185
Type: osv

## Details
Use-after-free vulnerability in the mg_http_multipart_wait_for_boundary function in mongoose.c in Cesanta Mongoose Embedded Web Server Library 6.7 and earlier and Mongoose OS 1.2 and earlier allows remote attackers to cause a denial of service (crash) via a multipart/form-data POST request without a MIME boundary string.

## References
- http://www.securityfocus.com/archive/1/540355/100/0/threaded
- https://www.exploit-db.com/exploits/41826/
- http://www.securityfocus.com/bid/97370
- https://github.com/cesanta/mongoose-os/commit/042eb437973a202d00589b13d628181c6de5cf5b
- https://github.com/cesanta/mongoose/commit/b8402ed0733e3f244588b61ad5fedd093e3cf9cc
- https://www.compass-security.com/fileadmin/Datein/Research/Advisories/CVE-2017-7185_mongoose_os_use_after_free.txt
