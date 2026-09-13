# [M] CVE-2017-8871

## Summary
Severity: Medium
Advisory: CVE-2017-8871
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-12
Source: https://osv.dev/vulnerability/CVE-2017-8871
Type: osv

## Details
The cr_parser_parse_selector_core function in cr-parser.c in libcroco 0.6.12 allows remote attackers to cause a denial of service (infinite loop and CPU consumption) via a crafted CSS file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00043.html
- https://bugzilla.gnome.org/show_bug.cgi?id=782649
- http://www.openwall.com/lists/oss-security/2020/08/13/3
- https://www.exploit-db.com/exploits/42147/
