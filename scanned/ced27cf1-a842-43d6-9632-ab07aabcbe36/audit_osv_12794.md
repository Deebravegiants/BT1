# [C] CVE-2018-14938

## Summary
Severity: Critical
Advisory: CVE-2018-14938
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-08-05
Source: https://osv.dev/vulnerability/CVE-2018-14938
Type: osv

## Details
An issue was discovered in wifipcap/wifipcap.cpp in TCPFLOW through 1.5.0-alpha. There is an integer overflow in the function handle_prism during caplen processing. If the caplen is less than 144, one can cause an integer overflow in the function handle_80211, which will result in an out-of-bounds read and may allow access to sensitive memory (or a denial of service).

## References
- https://lists.debian.org/debian-lts-announce/2020/11/msg00046.html
- https://usn.ubuntu.com/3955-1/
- https://github.com/simsong/tcpflow/commit/a4e1cd14eb5ccc51ed271b65b3420f7d692c40eb
- https://github.com/simsong/tcpflow/issues/182
