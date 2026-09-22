# [M] CVE-2020-8944

## Summary
Severity: Medium
Advisory: CVE-2020-8944
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8944
Type: osv

## Details
An arbitrary memory write vulnerability in Asylo versions up to 0.6.0 allows an untrusted attacker to make a call to ecall_restore using the attribute output which fails to check the range of a pointer. An attacker can use this pointer to write to arbitrary memory addresses including those within the secure enclave We recommend upgrading past commit 382da2b8b09cbf928668a2445efb778f76bd9c8a

## References
- https://github.com/google/asylo/commit/382da2b8b09cbf928668a2445efb778f76bd9c8a
