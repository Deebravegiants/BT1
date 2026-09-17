# [H] CVE-2018-20742

## Summary
Severity: High
Advisory: CVE-2018-20742
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-24
Source: https://osv.dev/vulnerability/CVE-2018-20742
Type: osv

## Details
An issue was discovered in UC Berkeley RISE Opaque before 2018-12-01. There is no boundary check on ocall_malloc. The return value could be a pointer to enclave memory. It could cause an arbitrary enclave memory write.

## References
- https://github.com/ucbrise/opaque/commit/5ddda15d89f5ac82f4416208c5319ace4aecdc36
- https://github.com/ucbrise/opaque/issues/66
