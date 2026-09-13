# [H] CVE-2022-33743

## Summary
Severity: High
Advisory: CVE-2022-33743
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/CVE-2022-33743
Type: osv

## Details
network backend may cause Linux netfront to use freed SKBs While adding logic to support XDP (eXpress Data Path), a code label was moved in a way allowing for SKBs having references (pointers) retained for further processing to nevertheless be freed.

## References
- https://www.debian.org/security/2022/dsa-5191
- https://xenbits.xenproject.org/xsa/advisory-405.txt
- http://www.openwall.com/lists/oss-security/2022/07/05/5
- http://xenbits.xen.org/xsa/advisory-405.html
