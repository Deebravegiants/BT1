# [C] CVE-2017-2885

## Summary
Severity: Critical
Advisory: CVE-2017-2885
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-2885
Type: osv

## Details
An exploitable stack based buffer overflow vulnerability exists in the GNOME libsoup 2.58. A specially crafted HTTP request can cause a stack overflow resulting in remote code execution. An attacker can send a special HTTP request to the vulnerable server to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/100258
- https://access.redhat.com/errata/RHSA-2017:2459
- https://www.debian.org/security/2017/dsa-3929
- http://packetstormsecurity.com/files/160388/ProCaster-LE-32F430-GStreamer-souphttpsrc-libsoup-2.51.3-Stack-Overflow.html
- http://seclists.org/fulldisclosure/2020/Dec/3
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0392
