# [C] CVE-2020-11684

## Summary
Severity: Critical
Advisory: CVE-2020-11684
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-09-14
Source: https://osv.dev/vulnerability/CVE-2020-11684
Type: osv

## Details
AT91bootstrap before 3.9.2 does not properly wipe encryption and authentication keys from memory before passing control to a less privileged software component. This can be exploited to disclose these keys and subsequently encrypt and sign the next boot stage (such as the bootloader).

## References
- https://github.com/linux4sam/at91bootstrap/commit/45419497309ffbf27c17ea7938499aca99168927
- https://labs.f-secure.com/advisories/microchip-at91bootstrap/
