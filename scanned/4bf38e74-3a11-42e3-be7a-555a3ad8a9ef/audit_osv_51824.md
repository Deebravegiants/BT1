# [H] CVE-2021-41457

## Summary
Severity: High
Advisory: CVE-2021-41457
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-01
Source: https://osv.dev/vulnerability/CVE-2021-41457
Type: osv

## Details
There is a stack buffer overflow in MP4Box 1.1.0 at src/filters/dmx_nhml.c in nhmldmx_init_parsing which leads to a denial of service vulnerability.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1909
