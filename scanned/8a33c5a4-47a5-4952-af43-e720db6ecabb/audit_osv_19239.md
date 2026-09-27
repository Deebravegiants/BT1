# [M] CVE-2020-8936

## Summary
Severity: Medium
Advisory: CVE-2020-8936
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8936
Type: osv

## Details
An arbitrary memory overwrite vulnerability in Asylo versions up to 0.6.0 allows an attacker to make a host call to UntrustedCall. UntrustedCall failed to validate the buffer range within sgx_params and allowed the host to return a pointer that was an address within the enclave memory. This allowed an attacker to read memory values from within the enclave.

## References
- https://github.com/google/asylo/commit/83036fd841d33baa7e039f842d131aa7881fdcc2
