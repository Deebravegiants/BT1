# [H] CVE-2021-44541

## Summary
Severity: High
Advisory: CVE-2021-44541
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-44541
Type: osv

## Details
A vulnerability was found in Privoxy which was fixed in process_encrypted_request_headers() by freeing header memory when failing to get the request destination.

## References
- https://www.privoxy.org/3.0.33/user-manual/whatsnew.html%2C
- https://www.privoxy.org/gitweb/?p=privoxy.git%3Ba=commit%3Bh=652b4b7cb0
