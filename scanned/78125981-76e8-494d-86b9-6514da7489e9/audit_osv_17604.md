# [C] CVE-2020-17467

## Summary
Severity: Critical
Advisory: CVE-2020-17467
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17467
Type: osv

## Details
An issue was discovered in FNET through 4.6.4. The code for processing the hostname from an LLMNR request doesn't check for '\0' termination. Therefore, the deduced length of the hostname doesn't reflect the correct length of the actual data. This may lead to Information Disclosure in _fnet_llmnr_poll in fnet_llmnr.c during a response to a malicious request of the DNS class IN.

## References
- http://fnet.sourceforge.net/manual/fnet_history.html
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
