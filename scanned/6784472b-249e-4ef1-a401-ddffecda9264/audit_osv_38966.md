# [H] media: mtk-mdp: Fix error handling in probe function

## Summary
Severity: High
Advisory: CVE-2026-43207
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43207
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mtk-mdp: Fix error handling in probe function

Add mtk_mdp_unregister_m2m_device() on the error handling path to prevent
resource leak.

Add check for the return value of vpu_get_plat_device() to prevent null
pointer dereference. And vpu_get_plat_device() increases the reference
count of the returned platform device. Add platform_device_put() to
prevent reference leak.

## References
- https://git.kernel.org/stable/c/0bc43eaf021347f8d5aba87712c36b799695eec6
- https://git.kernel.org/stable/c/12cafc15d24611bfb43c82877b1bbb7454a85d5a
- https://git.kernel.org/stable/c/2e8f53a7382943411557e370f1a4f3946624a30e
- https://git.kernel.org/stable/c/8a8a3232abac5b972058a5f2cb3e33199d2a8648
- https://git.kernel.org/stable/c/9d7962d5c81d6cf3f8dbdb5c71c57600bac5772b
- https://git.kernel.org/stable/c/9d9c67976eda502edc6b3a148a1c5b6a18b69a98
- https://git.kernel.org/stable/c/b3fc99fe5b25613dd61c57bc70b8479adff4f60d
- https://git.kernel.org/stable/c/c8737d33d4e8ffae87e5d5edac17f8a705235cc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43207.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43207
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
