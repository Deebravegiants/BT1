# [M] CVE-2021-47499

## Summary
Severity: Medium
Advisory: CVE-2021-47499
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47499
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: accel: kxcjk-1013: Fix possible memory leak in probe and remove

When ACPI type is ACPI_SMO8500, the data->dready_trig will not be set, the
memory allocated by iio_triggered_buffer_setup() will not be freed, and cause
memory leak as follows:

unreferenced object 0xffff888009551400 (size 512):
  comm "i2c-SMO8500-125", pid 911, jiffies 4294911787 (age 83.852s)
  hex dump (first 32 bytes):
    02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 20 e2 e5 c0 ff ff ff ff  ........ .......
  backtrace:
    [<0000000041ce75ee>] kmem_cache_alloc_trace+0x16d/0x360
    [<000000000aeb17b0>] iio_kfifo_allocate+0x41/0x130 [kfifo_buf]
    [<000000004b40c1f5>] iio_triggered_buffer_setup_ext+0x2c/0x210 [industrialio_triggered_buffer]
    [<000000004375b15f>] kxcjk1013_probe+0x10c3/0x1d81 [kxcjk_1013]

Fix it by remove data->dready_trig condition in probe and remove.

## References
- https://git.kernel.org/stable/c/8c163a14277115ca962103910ab4cce55e862ffb
- https://git.kernel.org/stable/c/8c1d43f3a3fc7184c42d7398bdf59a2a2903e4fc
- https://git.kernel.org/stable/c/a3730f74159ad00a28960c0efe2a931fe6fe6b45
- https://git.kernel.org/stable/c/ee86d0bad80bdcd11a87e188a596727f41b62320
- https://git.kernel.org/stable/c/14508fe13b1c578b3d2ba574f1d48b351975860c
- https://git.kernel.org/stable/c/3899700ddacbf7aaafadf44464fff3ff0d4e3307
- https://git.kernel.org/stable/c/60a55b9d91ba99eb8cf015bc46dc2de05e168a15
- https://git.kernel.org/stable/c/70c9774e180d151abaab358108e3510a8e615215
