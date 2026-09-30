# [C] CVE-2017-2921

## Summary
Severity: Critical
Advisory: CVE-2017-2921
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2921
Type: osv

## Details
An exploitable memory corruption vulnerability exists in the Websocket protocol implementation of Cesanta Mongoose 6.8. A specially crafted websocket packet can cause an integer overflow, leading to a heap buffer overflow and resulting in denial of service and potential remote code execution. An attacker needs to send a specially crafted websocket packet over network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0428
