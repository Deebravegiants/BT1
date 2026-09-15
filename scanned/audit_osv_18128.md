# [H] CVE-2020-24335

## Summary
Severity: High
Advisory: CVE-2020-24335
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-02
Source: https://osv.dev/vulnerability/CVE-2020-24335
Type: osv

## Details
An issue was discovered in uIP through 1.0, as used in Contiki and Contiki-NG. Domain name parsing lacks bounds checks, allowing an attacker to corrupt memory with crafted DNS packets.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
- https://github.com/adamdunkels/uip
- https://github.com/contiki-ng/contiki-ng
- https://github.com/contiki-os/contiki
