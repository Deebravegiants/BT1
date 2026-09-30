# [H] CVE-2021-3548

## Summary
Severity: High
Advisory: CVE-2021-3548
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-3548
Type: osv

## Details
A flaw was found in dmg2img through 20170502. dmg2img did not validate the size of the read buffer during memcpy() inside the main() function. This possibly leads to memory layout information leaking in the data. This might be used in a chain of vulnerability in order to reach code execution.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1959585
