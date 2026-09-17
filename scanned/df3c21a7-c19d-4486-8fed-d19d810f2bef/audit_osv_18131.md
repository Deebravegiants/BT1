# [H] CVE-2020-24339

## Summary
Severity: High
Advisory: CVE-2020-24339
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-24339
Type: osv

## Details
An issue was discovered in picoTCP and picoTCP-NG through 1.7.0. The DNS domain name record decompression functionality in pico_dns_decompress_name() in pico_dns_common.c does not validate the compression pointer offset values with respect to the actual data present in a DNS response packet, causing out-of-bounds reads that lead to Denial-of-Service.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
