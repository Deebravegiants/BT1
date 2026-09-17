# [H] hwmon: (ibmpex) Fix possible UAF when ibmpex_register_bmc() fails

## Summary
Severity: High
Advisory: CVE-2022-49029
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49029
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <4.9.335, >=4.10.0 <4.14.301, >=4.15.0 <4.19.268, >=4.20.0 <5.4.226, >=5.5.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (ibmpex) Fix possible UAF when ibmpex_register_bmc() fails

Smatch report warning as follows:

drivers/hwmon/ibmpex.c:509 ibmpex_register_bmc() warn:
  '&data->list' not removed from list

If ibmpex_find_sensors() fails in ibmpex_register_bmc(), data will
be freed, but data->list will not be removed from driver_data.bmc_data,
then list traversal may cause UAF.

Fix by removeing it from driver_data.bmc_data before free().

## References
- https://git.kernel.org/stable/c/24b9633f7db7f4809be7053df1d2e117e7c2de10
- https://git.kernel.org/stable/c/45f6e81863747c0d7bc6a95ec51129900e71467a
- https://git.kernel.org/stable/c/798198273bf86673b970b51acdb35e57f42b3fcb
- https://git.kernel.org/stable/c/7b2b67fe1339389e0bf3c37c7a677a004ac0e4e3
- https://git.kernel.org/stable/c/90907cd4d11351ff76c9a447bcb5db0e264c47cd
- https://git.kernel.org/stable/c/e2a87785aab0dac190ac89be6a9ba955e2c634f2
- https://git.kernel.org/stable/c/e65cfd1f9cd27d9c27ee5cb88128a9f79f25d863
- https://git.kernel.org/stable/c/f2a13196ad41c6c2ab058279dffe6c97292e753a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49029.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49029
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
