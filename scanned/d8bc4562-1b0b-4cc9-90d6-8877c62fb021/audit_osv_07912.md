# [M] UAF and double free in MQTT sending

## Summary
Severity: Medium
Advisory: CURL-CVE-2021-22945
Aliases: CVE-2021-22945
Published: 2021-09-15
Source: https://osv.dev/vulnerability/CURL-CVE-2021-22945
Type: osv

## Details
When sending data to an MQTT server, libcurl could in some circumstances
erroneously keep a pointer to an already freed memory area and both use that
again in a subsequent call to send data and also free it *again*.
