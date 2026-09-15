# [M] CVE-2021-22552

## Summary
Severity: Medium
Advisory: CVE-2021-22552
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-02
Source: https://osv.dev/vulnerability/CVE-2021-22552
Type: osv

## Details
An untrusted memory read vulnerability in Asylo versions up to 0.6.1 allows an untrusted attacker to pass a syscall number in MessageReader that is then used by sysno() and can bypass validation. This can allow the attacker to read memory from within the secure enclave. We recommend updating to Asylo 0.6.3 or past https://github.com/google/asylo/commit/90d7619e9dd99bcdb6cd28c7649d741d254d9a1a

## References
- https://github.com/google/asylo/commit/90d7619e9dd99bcdb6cd28c7649d741d254d9a1a
