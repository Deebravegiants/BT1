# [H] CVE-2019-19331

## Summary
Severity: High
Advisory: CVE-2019-19331
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-16
Source: https://osv.dev/vulnerability/CVE-2019-19331
Type: osv

## Details
knot-resolver before version 4.3.0 is vulnerable to denial of service through high CPU utilization. DNS replies with very many resource records might be processed very inefficiently, in extreme cases taking even several CPU seconds for each such uncached message. For example, a few thousand A records can be squashed into one DNS message (limit is 64kB).

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00017.html
- https://www.knot-resolver.cz/2019-12-04-knot-resolver-4.3.0.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-19331
