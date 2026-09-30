# [H] CVE-2021-43612

## Summary
Severity: High
Advisory: CVE-2021-43612
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2021-43612
Type: osv

## Details
In lldpd before 1.0.13, when decoding SONMP packets in the sonmp_decode function, it's possible to trigger an out-of-bounds heap read via short SONMP packets.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3T5XHPOGIPWCRRPJUE6P3HVC5PTSD5JS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYA4AMJXCNF6UPFG36L2TPPT32C242SP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SKQWHG2SZJZSGC7PXVDAEJYBN7ESDR7D/
- https://github.com/lldpd/lldpd/commit/73d42680fce8598324364dbb31b9bc3b8320adf7
- https://github.com/lldpd/lldpd/compare/1.0.12...1.0.13
- https://lldpd.github.io/security.html
