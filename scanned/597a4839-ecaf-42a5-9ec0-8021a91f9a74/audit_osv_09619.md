# [M] CVE-2017-1000413

## Summary
Severity: Medium
Advisory: CVE-2017-1000413
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-02
Source: https://osv.dev/vulnerability/CVE-2017-1000413
Type: osv

## Details
Linaro's open source TEE solution called OP-TEE, version 2.4.0 (and older) is vulnerable a timing attack in the Montgomery parts of libMPA in OP-TEE resulting in a compromised private RSA key.

## References
- https://github.com/OP-TEE/optee_os/blob/2.5.0/CHANGELOG.md
- https://github.com/OP-TEE/optee_os/pull/1610
- https://www.op-tee.org/security-advisories/
