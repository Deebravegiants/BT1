# [M] CVE-2021-46944

## Summary
Severity: Medium
Advisory: CVE-2021-46944
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46944
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: staging/intel-ipu3: Fix memory leak in imu_fmt

We are losing the reference to an allocated memory if try. Change the
order of the check to avoid that.

## References
- https://git.kernel.org/stable/c/14d0e99c3ef6b0648535a31bf2eaabb4eff97b9e
- https://git.kernel.org/stable/c/3630901933afba1d16c462b04d569b7576339223
- https://git.kernel.org/stable/c/517f6f570566a863c2422b843c8b7d099474f6a9
- https://git.kernel.org/stable/c/74ba0adb5e983503b18a96121d965cad34ac7ce3
- https://git.kernel.org/stable/c/ff792ae52005c85a2d829c153e08d99a356e007d
