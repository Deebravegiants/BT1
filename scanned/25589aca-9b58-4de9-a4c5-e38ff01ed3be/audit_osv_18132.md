# [H] CVE-2020-24340

## Summary
Severity: High
Advisory: CVE-2020-24340
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-24340
Type: osv

## Details
An issue was discovered in picoTCP and picoTCP-NG through 1.7.0. The code that processes DNS responses in pico_mdns_handle_data_as_answers_generic() in pico_mdns.c does not check whether the number of answers/responses specified in a DNS packet header corresponds to the response data available in the packet, leading to an out-of-bounds read, invalid pointer dereference, and Denial-of-Service.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
