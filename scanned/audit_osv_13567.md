# [C] CVE-2018-20355

## Summary
Severity: Critical
Advisory: CVE-2018-20355
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-10
Source: https://osv.dev/vulnerability/CVE-2018-20355
Type: osv

## Details
An invalid write of 8 bytes due to a use-after-free vulnerability in the mg_http_free_proto_data_cgi function call in mongoose.c in Cesanta Mongoose Embedded Web Server Library 6.13 and earlier allows a denial of service (application crash) or remote code execution.

## References
- https://github.com/insi2304/mongoose-6.13-fuzz/blob/master/Simplest_Web_Server_Use_After_Free-mg_http_free_proto_data_cgi.png
