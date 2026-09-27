# [H] CVE-2021-31439

## Summary
Severity: High
Advisory: CVE-2021-31439
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-21
Source: https://osv.dev/vulnerability/CVE-2021-31439
Type: osv

## Details
This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of Synology DiskStation Manager. Authentication is not required to exploit this vulnerablity. The specific flaw exists within the processing of DSI structures in Netatalk. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-12326.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00018.html
- https://www.debian.org/security/2023/dsa-5503
- https://www.synology.com/zh-hk/security/advisory/Synology_SA_20_26
- https://www.zerodayinitiative.com/advisories/ZDI-21-492/
- https://security.gentoo.org/glsa/202311-02
