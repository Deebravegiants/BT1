# [H] CVE-2018-10945

## Summary
Severity: High
Advisory: CVE-2018-10945
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-10945
Type: osv

## Details
The mg_handle_cgi function in mongoose.c in Mongoose 6.11 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash, or NULL pointer dereference) via an HTTP request, related to the mbuf_insert function.

## References
- http://blog.hac425.top/2018/05/16/CVE-2018-10945-mongoose.html
