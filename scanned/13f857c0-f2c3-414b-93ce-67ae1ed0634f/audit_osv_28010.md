# [H] crypto: qat - resolve race condition during AER recovery

## Summary
Severity: High
Advisory: CVE-2024-26974
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26974
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - resolve race condition during AER recovery

During the PCI AER system's error recovery process, the kernel driver
may encounter a race condition with freeing the reset_data structure's
memory. If the device restart will take more than 10 seconds the function
scheduling that restart will exit due to a timeout, and the reset_data
structure will be freed. However, this data structure is used for
completion notification after the restart is completed, which leads
to a UAF bug.

This results in a KFENCE bug notice.

  BUG: KFENCE: use-after-free read in adf_device_reset_worker+0x38/0xa0 [intel_qat]
  Use-after-free read at 0x00000000bc56fddf (in kfence-#142):
  adf_device_reset_worker+0x38/0xa0 [intel_qat]
  process_one_work+0x173/0x340

To resolve this race condition, the memory associated to the container
of the work_struct is freed on the worker if the timeout expired,
otherwise on the function that schedules the worker.
The timeout detection can be done by checking if the caller is
still waiting for completion or not by using completion_done() function.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0c2cf5142bfb634c0ef0a1a69cdf37950747d0be
- https://git.kernel.org/stable/c/226fc408c5fcd23cc4186f05ea3a09a7a9aef2f7
- https://git.kernel.org/stable/c/4ae5a97781ce7d6ecc9c7055396535815b64ca4f
- https://git.kernel.org/stable/c/7d42e097607c4d246d99225bf2b195b6167a210c
- https://git.kernel.org/stable/c/8a5a7611ccc7b1fba8d933a9f22a2e76859d94dc
- https://git.kernel.org/stable/c/8e81cd58aee14a470891733181a47d123193ba81
- https://git.kernel.org/stable/c/bb279ead42263e9fb09480f02a4247b2c287d828
- https://git.kernel.org/stable/c/d03092550f526a79cf1ade7f0dfa74906f39eb71
- https://git.kernel.org/stable/c/daba62d9eeddcc5b1081be7d348ca836c83c59d7
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26974.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
