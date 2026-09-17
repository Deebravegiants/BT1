# [M] CVE-2019-17420

## Summary
Severity: Medium
Advisory: CVE-2019-17420
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-10-10
Source: https://osv.dev/vulnerability/CVE-2019-17420
Type: osv

## Details
In OISF LibHTP before 0.5.31, as used in Suricata 4.1.4 and other products, an HTTP protocol parsing error causes the http_header signature to not alert on a response with a single \r\n ending.

## References
- https://redmine.openinfosecfoundation.org/issues/2969
- https://github.com/OISF/libhtp/compare/0.5.30...0.5.31
- https://github.com/OISF/libhtp/pull/213
