# [H] CVE-2020-8935

## Summary
Severity: High
Advisory: CVE-2020-8935
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8935
Type: osv

## Details
An arbitrary memory overwrite vulnerability in Asylo versions up to 0.6.0 allow an attacker to make an Ecall_restore function call to reallocate untrusted code and overwrite sections of the Enclave memory address. We recommend updating your library.

## References
- https://github.com/google/asylo/commit/ed0926bff0e423cd122a18b3d2fc772817f66825
