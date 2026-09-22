# [C] CVE-2020-8904

## Summary
Severity: Critical
Advisory: CVE-2020-8904
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/CVE-2020-8904
Type: osv

## Details
An arbitrary memory overwrite vulnerability in the trusted memory of Asylo exists in versions prior to 0.6.0. As the ecall_restore function fails to validate the range of the output_len pointer, an attacker can manipulate the tmp_output_len value and write to an arbitrary location in the trusted (enclave) memory. We recommend updating Asylo to version 0.6.0 or later.

## References
- https://github.com/google/asylo/commit/e582f36ac49ee11a21d23ad6a30c333092e0a94e
