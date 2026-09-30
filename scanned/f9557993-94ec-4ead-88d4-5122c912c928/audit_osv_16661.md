# [H] CVE-2019-8922

## Summary
Severity: High
Advisory: CVE-2019-8922
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-29
Source: https://osv.dev/vulnerability/CVE-2019-8922
Type: osv

## Details
A heap-based buffer overflow was discovered in bluetoothd in BlueZ through 5.48. There isn't any check on whether there is enough space in the destination buffer. The function simply appends all data passed to it. The values of all attributes that are requested are appended to the output buffer. There are no size checks whatsoever, resulting in a simple heap overflow if one can craft a request where the response is large enough to overflow the preallocated buffer. This issue exists in service_attr_req gets called by process_request (in sdpd-request.c), which also allocates the response buffer.

## References
- https://lists.debian.org/debian-lts-announce/2022/10/msg00026.html
- https://security.netapp.com/advisory/ntap-20211203-0002/
- https://ssd-disclosure.com/ssd-advisory-linux-bluez-information-leak-and-heap-overflow/
