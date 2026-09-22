# [M] CVE-2021-44421

## Summary
Severity: Medium
Advisory: CVE-2021-44421
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-44421
Type: osv

## Details
The pointer-validation logic in util/mem_util.rs in Occlum before 0.26.0 for Intel SGX acts as a confused deputy that allows a local attacker to access unauthorized information via side-channel analysis.

## References
- https://github.com/occlum/occlum/compare/0.25.0...v0.26.0
- https://github.com/occlum/occlum/commit/36918e42bf6732c4d3996bc99eb013eb6b90b249
- https://github.com/occlum/occlum/blob/821ea843ae21037e6cff5268306d2da1fb131552/src/libos/src/util/mem_util.rs#L130
- https://github.com/occlum/occlum/blob/821ea843ae21037e6cff5268306d2da1fb131552/src/libos/src/util/mem_util.rs#L51
