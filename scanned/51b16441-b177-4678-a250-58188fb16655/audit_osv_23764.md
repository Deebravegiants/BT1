# [M] thermal/drivers/broadcom: Fix potential NULL dereference in sr_thermal_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49459
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49459
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal/drivers/broadcom: Fix potential NULL dereference in sr_thermal_probe

platform_get_resource() may return NULL, add proper check to
avoid potential NULL dereferencing.

## References
- https://git.kernel.org/stable/c/61621e042c22b47d1eadee617bdd26835294b425
- https://git.kernel.org/stable/c/79098339ac2065f4b4352ef5921628970b6f47e6
- https://git.kernel.org/stable/c/b3461ccaa5d2588568d865faee285512ad448049
- https://git.kernel.org/stable/c/e20d136ec7d6f309989c447638365840d3424c8e
- https://git.kernel.org/stable/c/ee9b6b02e8c140323ed46d6602d805ea735c7719
- https://git.kernel.org/stable/c/ef1235c6514a58f274246cf4a2d5f4e40af539ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49459.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49459
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
