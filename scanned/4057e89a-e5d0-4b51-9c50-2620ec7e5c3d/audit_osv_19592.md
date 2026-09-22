# [H] CVE-2021-22550

## Summary
Severity: High
Advisory: CVE-2021-22550
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-22550
Type: osv

## Details
An attacker can modify the pointers in enclave memory to overwrite arbitrary memory addresses within the secure enclave. It is recommended to update past 0.6.3 or git commit https://github.com/google/asylo/commit/a47ef55db2337d29de19c50cd29b0deb2871d31c

## References
- https://github.com/google/asylo/commit/a47ef55db2337d29de19c50cd29b0deb2871d31c
