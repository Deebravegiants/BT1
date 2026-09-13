# [C] nvmet: avoid potential UAF in nvmet_req_complete()

## Summary
Severity: Critical
Advisory: CVE-2023-53116
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53116
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.14.311, >=4.15.0 <4.19.279, >=4.20.0 <5.4.238, >=5.5.0 <5.10.176, >=5.11.0 <5.15.104, >=5.16.0 <6.1.21, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: avoid potential UAF in nvmet_req_complete()

An nvme target ->queue_response() operation implementation may free the
request passed as argument. Such implementation potentially could result
in a use after free of the request pointer when percpu_ref_put() is
called in nvmet_req_complete().

Avoid such problem by using a local variable to save the sq pointer
before calling __nvmet_req_complete(), thus avoiding dereferencing the
req pointer after that function call.

## References
- https://git.kernel.org/stable/c/04c394208831d5e0d5cfee46722eb0f033cd4083
- https://git.kernel.org/stable/c/6173a77b7e9d3e202bdb9897b23f2a8afe7bf286
- https://git.kernel.org/stable/c/8ed9813871038b25a934b21ab76b5b7dbf44fc3a
- https://git.kernel.org/stable/c/a6317235da8aa7cb97529ebc8121cc2a4c4c437a
- https://git.kernel.org/stable/c/bcd535f07c58342302a2cd2bdd8894fe0872c8a9
- https://git.kernel.org/stable/c/e5d99b29012bbf0e86929403209723b2806500c1
- https://git.kernel.org/stable/c/f1d5888a5efe345b63c430b256e95acb0a475642
- https://git.kernel.org/stable/c/fafcb4b26393870c45462f9af6a48e581dbbcf7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53116.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
