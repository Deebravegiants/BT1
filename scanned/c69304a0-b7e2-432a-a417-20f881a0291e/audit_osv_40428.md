# [H] mm/huge_memory: update file PMD counter before folio_put()

## Summary
Severity: High
Advisory: CVE-2026-53189
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53189
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/huge_memory: update file PMD counter before folio_put()

__split_huge_pmd_locked() updates the file/shmem RSS counter after
dropping the PMD mapping's folio reference.  If folio_put() drops the last
reference, mm_counter_file() can later read freed folio state via
folio_test_swapbacked().

Move the counter update before folio_put().

## References
- https://git.kernel.org/stable/c/108963978a681c0c468d279cac2b930c27672877
- https://git.kernel.org/stable/c/459771c9cf30f378bdbd30fc65d17f7eb931bb59
- https://git.kernel.org/stable/c/5f5b604e1e6bde4e889199168ee80fe8306d06ad
- https://git.kernel.org/stable/c/6c29a8ba084e89499ca77b947e07ae817f9c16ce
- https://git.kernel.org/stable/c/84b3212b166b446faea27ebebb7161405ffceef9
- https://git.kernel.org/stable/c/8d878059924f12c1bc24556a92ec56add74de3c8
- https://git.kernel.org/stable/c/ae9d4caf6f133e884cf5fcda4982c493b35e5194
- https://git.kernel.org/stable/c/ed5b030931292c94133437ac5e5ff580e498eabd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53189.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53189
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
