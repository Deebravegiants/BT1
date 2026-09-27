# [H] CVE-2021-20226

## Summary
Severity: High
Advisory: CVE-2021-20226
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-20226
Type: osv

## Details
A use-after-free flaw was found in the io_uring in Linux kernel, where a local attacker with a user privilege could cause a denial of service problem on the system The issue results from the lack of validating the existence of an object prior to performing operations on the object by not incrementing the file reference counter while in use. The highest threat from this vulnerability is to data integrity, confidentiality and system availability.

## References
- https://security.netapp.com/advisory/ntap-20210401-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1873476
