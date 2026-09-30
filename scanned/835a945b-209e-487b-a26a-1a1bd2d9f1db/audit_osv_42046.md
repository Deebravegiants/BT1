# [C] ksmbd: serialize QUERY_DIRECTORY requests per file

## Summary
Severity: Critical
Advisory: CVE-2026-64397
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64397
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: serialize QUERY_DIRECTORY requests per file

smb2_query_dir() stores a pointer to its stack-allocated private data in
the ksmbd_file readdir_data. Concurrent QUERY_DIRECTORY requests using the
same file handle can overwrite this pointer while an iterate_dir() callback
is still using it, resulting in a stack use-after-free.

Add a per-file mutex and hold it while accessing the shared directory
enumeration state. The lock covers scan restart, dot entry state,
readdir_data setup and iteration, and response construction. This prevents
another request from replacing readdir_data.private before the current
request has finished using it and also serializes the shared file position.

## References
- https://git.kernel.org/stable/c/1426fd79102539bc0ab5c8fced047ad4313b9908
- https://git.kernel.org/stable/c/2a64dbf9c739ddf7a25a066507597bf89f8f73d2
- https://git.kernel.org/stable/c/64dac2d486ec1eb18dc00968b16a230b6b75ec24
- https://git.kernel.org/stable/c/a1d5d31cad593ea5e1b637f2f39c9ef6d09d1199
- https://git.kernel.org/stable/c/be6d26bf27499977c746abc163659915082348d8
- https://git.kernel.org/stable/c/fd22b039a5a05bc1d6818e9dcd1001fb432a829d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64397.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
