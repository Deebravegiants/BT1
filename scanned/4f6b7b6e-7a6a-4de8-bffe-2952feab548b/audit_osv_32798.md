# [H] netfilter: ipset: fix region locking in hash types

## Summary
Severity: High
Advisory: CVE-2025-37997
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-37997
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.294, >=5.5.0 <5.10.238, >=5.6.0 <5.15.183, >=5.11.0 <6.1.139, >=5.16.0 <6.6.91, >=6.2.0 <6.12.29, >=6.7.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: fix region locking in hash types

Region locking introduced in v5.6-rc4 contained three macros to handle
the region locks: ahash_bucket_start(), ahash_bucket_end() which gave
back the start and end hash bucket values belonging to a given region
lock and ahash_region() which should give back the region lock belonging
to a given hash bucket. The latter was incorrect which can lead to a
race condition between the garbage collector and adding new elements
when a hash type of set is defined with timeouts.

## References
- https://git.kernel.org/stable/c/00cfc5fad1491796942a948808afb968a0a3f35b
- https://git.kernel.org/stable/c/226ce0ec38316d9e3739e73a64b6b8304646c658
- https://git.kernel.org/stable/c/6e002ecc1c8cfdfc866b9104ab7888da54613e59
- https://git.kernel.org/stable/c/82c1eb32693bc48251d92532975e19160987e5b9
- https://git.kernel.org/stable/c/8478a729c0462273188263136880480729e9efca
- https://git.kernel.org/stable/c/a3dfec485401943e315c394c29afe2db8f9481d6
- https://git.kernel.org/stable/c/aa77294b0f73bb8265987591460cd25b8722c3df
- https://git.kernel.org/stable/c/e2ab67672b2288521a6146034a971f9a82ffc5c5
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37997.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
