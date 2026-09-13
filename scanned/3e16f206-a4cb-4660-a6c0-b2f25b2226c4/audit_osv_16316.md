# [H] CVE-2019-5164

## Summary
Severity: High
Advisory: CVE-2019-5164
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-5164
Type: osv

## Details
An exploitable code execution vulnerability exists in the ss-manager binary of Shadowsocks-libev 3.3.2. Specially crafted network packets sent to ss-manager can cause an arbitrary binary to run, resulting in code execution and privilege escalation. An attacker can send network packets to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00061.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0958
