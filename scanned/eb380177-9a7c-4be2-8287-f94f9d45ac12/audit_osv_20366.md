# [C] CVE-2021-33304

## Summary
Severity: Critical
Advisory: CVE-2021-33304
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-15
Source: https://osv.dev/vulnerability/CVE-2021-33304
Type: osv

## Details
Double Free vulnerability in virtualsquare picoTCP v1.7.0 and picoTCP-NG v2.1 in modules/pico_fragments.c in function pico_fragments_reassemble, allows attackers to execute arbitrary code.

## References
- https://github.com/virtualsquare/picotcp/issues/6
