# [M] CVE-2020-21676

## Summary
Severity: Medium
Advisory: CVE-2020-21676
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2020-21676
Type: osv

## Details
A stack-based buffer overflow in the genpstrx_text() component in genpstricks.c of fig2dev 3.2.7b allows attackers to cause a denial of service (DOS) via converting a xfig file into pstricks format.

## References
- https://cwe.mitre.org/data/definitions/121.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00002.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00044.html
- https://sourceforge.net/p/mcj/tickets/76/
