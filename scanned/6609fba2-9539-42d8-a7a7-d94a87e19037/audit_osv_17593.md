# [H] CVE-2020-17439

## Summary
Severity: High
Advisory: CVE-2020-17439
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17439
Type: osv

## Details
An issue was discovered in uIP 1.0, as used in Contiki 3.0 and other products. The code that parses incoming DNS packets does not validate that the incoming DNS replies match outgoing DNS queries in newdata() in resolv.c. Also, arbitrary DNS replies are parsed if there was any outgoing DNS query with a transaction ID that matches the transaction ID of an incoming reply. Provided that the default DNS cache is quite small (only four records) and that the transaction ID has a very limited set of values that is quite easy to guess, this can lead to DNS cache poisoning.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
