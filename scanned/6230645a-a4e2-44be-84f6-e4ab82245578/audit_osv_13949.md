# [H] CVE-2018-5739

## Summary
Severity: High
Advisory: CVE-2018-5739
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5739
Type: osv

## Details
An extension to hooks capabilities which debuted in Kea 1.4.0 introduced a memory leak for operators who are using certain hooks library facilities. In order to support multiple requests simultaneously, Kea 1.4 added a callout handle store but unfortunately the initial implementation of this store does not properly free memory in every case. Hooks which make use of query4 or query6 parameters in their callouts can leak memory, resulting in the eventual exhaustion of available memory and subsequent failure of the server process. Affects Kea DHCP 1.4.0.

## References
- https://kb.isc.org/docs/aa-01626
