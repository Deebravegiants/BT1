# [M] CVE-2019-9547

## Summary
Severity: Medium
Advisory: CVE-2019-9547
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-03-01
Source: https://osv.dev/vulnerability/CVE-2019-9547
Type: osv

## Details
In Storage Performance Development Kit (SPDK) before 19.01, a malicious vhost client (i.e., virtual machine) could carefully construct a circular descriptor chain that would result in a partial denial of service in the SPDK vhost target, because the vhost target did not properly detect such chains.

## References
- https://github.com/spdk/spdk/commit/eca42c66092b9031711afe215fbc1891ee55f143
- https://github.com/spdk/spdk/releases/tag/v19.01
