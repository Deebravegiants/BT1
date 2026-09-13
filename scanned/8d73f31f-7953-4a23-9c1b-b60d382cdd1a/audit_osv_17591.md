# [H] CVE-2020-17437

## Summary
Severity: High
Advisory: CVE-2020-17437
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17437
Type: osv

## Details
An issue was discovered in uIP 1.0, as used in Contiki 3.0 and other products. When the Urgent flag is set in a TCP packet, and the stack is configured to ignore the urgent data, the stack attempts to use the value of the Urgent pointer bytes to separate the Urgent data from the normal data, by calculating the offset at which the normal data should be present in the global buffer. However, the length of this offset is not checked; therefore, for large values of the Urgent pointer bytes, the data pointer can point to memory that is way beyond the data buffer in uip_process in uip.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
- https://cert-portal.siemens.com/productcert/pdf/ssa-541018.pdf
