# [H] CVE-2021-22548

## Summary
Severity: High
Advisory: CVE-2021-22548
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-22548
Type: osv

## Details
An attacker can change the pointer to untrusted memory to point to trusted memory region which causes copying trusted memory to trusted memory, if the latter is later copied out, it allows for reading of memory regions from the trusted region. It is recommended to update past 0.6.2 or git commit https://github.com/google/asylo/commit/53ed5d8fd8118ced1466e509606dd2f473707a5c

## References
- https://github.com/google/asylo/commit/53ed5d8fd8118ced1466e509606dd2f473707a5c
