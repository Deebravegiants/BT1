# [H] CVE-2019-15767

## Summary
Severity: High
Advisory: CVE-2019-15767
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-15767
Type: osv

## Details
In GNU Chess 6.2.5, there is a stack-based buffer overflow in the cmd_load function in frontend/cmd.cc via a crafted chess position in an EPD file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ZA4UCVURQXNLUNFAMRLZBAFRHSEVC6Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TB4FURVE4C35UDXGAAHJL5NIHJQ3WDZT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TGIICRUZRFAK5M7SNHZKR7SKE77SFKWE/
- https://lists.gnu.org/archive/html/bug-gnu-chess/2019-08/msg00004.html
- https://lists.gnu.org/archive/html/bug-gnu-chess/2019-08/msg00005.html
