# [M] ALPINE-CVE-2016-6512

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6512
Ecosystem: Alpine:v3.5
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6512
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.0.5-r0

## Details
epan/dissectors/packet-wap.c in Wireshark 2.x before 2.0.5 omits an overflow check in the tvb_get_guintvar function, which allows remote attackers to cause a denial of service (infinite loop) via a crafted packet, related to the MMSE, WAP, WBXML, and WSP dissectors.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6512
