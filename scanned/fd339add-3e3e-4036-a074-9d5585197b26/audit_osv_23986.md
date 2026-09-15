# [H] iio: adc: mp2629: fix potential array out of bound access

## Summary
Severity: High
Advisory: CVE-2022-49792
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49792
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.156, >=5.11.0 <5.15.80, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: mp2629: fix potential array out of bound access

Add sentinel at end of maps to avoid potential array out of
bound access in iio core.

## References
- https://git.kernel.org/stable/c/1678d4abb2dc2ca3b05b998a9d88616976e4f947
- https://git.kernel.org/stable/c/399b2105a2240e730b9f3880bd8f154247539aa7
- https://git.kernel.org/stable/c/ca1547ab15f48dc81624183ae17a2fd1bad06dfc
- https://git.kernel.org/stable/c/d95b85c5084ad70011988861ee864529eefa1da0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49792.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49792
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
