# [M] CVE-2019-8921

## Summary
Severity: Medium
Advisory: CVE-2019-8921
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-11-29
Source: https://osv.dev/vulnerability/CVE-2019-8921
Type: osv

## Details
An issue was discovered in bluetoothd in BlueZ through 5.48. The vulnerability lies in the handling of a SVC_ATTR_REQ by the SDP implementation. By crafting a malicious CSTATE, it is possible to trick the server into returning more bytes than the buffer actually holds, resulting in leaking arbitrary heap data. The root cause can be found in the function service_attr_req of sdpd-request.c. The server does not check whether the CSTATE data is the same in consecutive requests, and instead simply trusts that it is the same.

## References
- https://lists.debian.org/debian-lts-announce/2022/10/msg00026.html
- https://security.netapp.com/advisory/ntap-20211203-0002/
- https://ssd-disclosure.com/ssd-advisory-linux-bluez-information-leak-and-heap-overflow/
