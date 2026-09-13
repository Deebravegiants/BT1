# [M] CVE-2022-3854

## Summary
Severity: Medium
Advisory: CVE-2022-3854
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-3854
Type: osv

## Details
A flaw was found in Ceph, relating to the URL processing on RGW backends. An attacker can exploit the URL processing by providing a null URL to crash the RGW, causing a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2139925
