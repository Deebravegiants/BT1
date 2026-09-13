# [H] libceph: guard missing CRUSH type name lookup

## Summary
Severity: High
Advisory: CVE-2026-68157
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68157
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: guard missing CRUSH type name lookup

Localized read selection can walk a parent bucket whose name exists in
the CRUSH map while its type has no matching entry in type_names.
get_immediate_parent() then dereferences a NULL type_cn and passes an
invalid pointer into strcmp(), causing a null-ptr-deref.

Skip such malformed parent buckets unless both the bucket name and type
name metadata are present. This keeps malformed hierarchy data from
crashing locality lookup and safely falls back to "not local".

[ idryomov: add WARN_ON_ONCE ]

## References
- https://git.kernel.org/stable/c/3767c9f0c1bbd98dd25cb088356a0fc6c1f09f50
- https://git.kernel.org/stable/c/4716a64b7cc2797741f7be4e283ace78a9dff37d
- https://git.kernel.org/stable/c/6a4b75d90f0cfbf22c14742ab35a803bc13f36ec
- https://git.kernel.org/stable/c/8ff579ac03d6e9d17d6d9c8443110167c14a382d
- https://git.kernel.org/stable/c/bbeae12fda3384a90fbebc8a19ba9d33f85b5361
- https://git.kernel.org/stable/c/c46d82c47afc968d6ee8ef4470fa2dd35b765c21
- https://git.kernel.org/stable/c/cbfcba275326c8c7dae9acd8f4a0d4c316fdafb0
- https://git.kernel.org/stable/c/db9cc9fd9660b2d69ee66f5a4cbec83c21a1c64d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68157.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68157
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
