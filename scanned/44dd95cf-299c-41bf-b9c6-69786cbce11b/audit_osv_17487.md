# [C] CVE-2020-15472

## Summary
Severity: Critical
Advisory: CVE-2020-15472
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-07-01
Source: https://osv.dev/vulnerability/CVE-2020-15472
Type: osv

## Details
In nDPI through 3.2, the H.323 dissector is vulnerable to a heap-based buffer over-read in ndpi_search_h323 in lib/protocols/h323.c, as demonstrated by a payload packet length that is too short.

## References
- https://lists.debian.org/debian-lts-announce/2022/08/msg00016.html
- https://github.com/ntop/nDPI/commit/b7e666e465f138ae48ab81976726e67deed12701
