# [H] CVE-2019-6963

## Summary
Severity: High
Advisory: CVE-2019-6963
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-6963
Type: osv

## Details
A heap-based buffer overflow in cosa_dhcpv4_dml.c in the RDK RDKB-20181217-1 CcspPandM module may allow attackers with login credentials to achieve remote code execution by crafting a long buffer in the "Comment" field of an IP reservation form in the admin panel. This is related to the CcspCommonLibrary module.

## References
- https://dojo.bullguard.com/dojo-by-bullguard/blog/the-gateway-is-wide-open
