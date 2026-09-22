# [M] md/raid10: fix wrong setting of max_corr_read_errors

## Summary
Severity: Medium
Advisory: CVE-2023-53313
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53313
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: fix wrong setting of max_corr_read_errors

There is no input check when echo md/max_read_errors and overflow might
occur. Add check of input number.

## References
- https://git.kernel.org/stable/c/025fde32fb957a5c271711bc66841f817ff5f299
- https://git.kernel.org/stable/c/05d10428e8dffed0bac2502f34151729fc189cd3
- https://git.kernel.org/stable/c/31c805a44b7569ca1017a4714385182d98bba212
- https://git.kernel.org/stable/c/3c76920e547d4b931bed758bad83fd658dd88b4e
- https://git.kernel.org/stable/c/74050a3fdd4aecfd2cbf74d3c145812ab2744375
- https://git.kernel.org/stable/c/aef6e98eb772594edd4399625e4e1bbe45971fa1
- https://git.kernel.org/stable/c/b1d8f38310bce3282374983b229d94edbaf1e570
- https://git.kernel.org/stable/c/e83cb411aa1c6c9617db9329897f4506ba9e9b9d
- https://git.kernel.org/stable/c/f8b20a405428803bd9881881d8242c9d72c6b2b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53313.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53313
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
