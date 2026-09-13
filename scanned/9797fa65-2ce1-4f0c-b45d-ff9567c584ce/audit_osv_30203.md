# [M] cpufreq: loongson3: Use raw_smp_processor_id() in do_service_request()

## Summary
Severity: Medium
Advisory: CVE-2024-50178
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50178
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpufreq: loongson3: Use raw_smp_processor_id() in do_service_request()

Use raw_smp_processor_id() instead of plain smp_processor_id() in
do_service_request(), otherwise we may get some errors with the driver
enabled:

 BUG: using smp_processor_id() in preemptible [00000000] code: (udev-worker)/208
 caller is loongson3_cpufreq_probe+0x5c/0x250 [loongson3_cpufreq]

## References
- https://git.kernel.org/stable/c/2b7ec33e534f7a10033a5cf07794acf48b182bbe
- https://git.kernel.org/stable/c/2f78e4a6d2702ac03c2bf2ed3a0e344e1fa9f967
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50178.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
