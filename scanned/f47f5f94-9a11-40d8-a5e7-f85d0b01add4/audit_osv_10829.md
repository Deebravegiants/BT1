# [C] CVE-2017-2922

## Summary
Severity: Critical
Advisory: CVE-2017-2922
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2922
Type: osv

## Details
An exploitable memory corruption vulnerability exists in the Websocket protocol implementation of Cesanta Mongoose 6.8. A specially crafted websocket packet can cause a buffer to be allocated while leaving stale pointers which leads to a use-after-free vulnerability which can be exploited to achieve remote code execution. An attacker needs to send a specially crafted websocket packet over the network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0429
