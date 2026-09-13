# [H] perf: arm_spe: Prevent overflow in PERF_IDX2OFF()

## Summary
Severity: High
Advisory: CVE-2025-40081
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40081
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: arm_spe: Prevent overflow in PERF_IDX2OFF()

Cast nr_pages to unsigned long to avoid overflow when handling large
AUX buffer sizes (>= 2 GiB).

## References
- https://git.kernel.org/stable/c/1a19ba8e1f4ff24ece8ca69b79df8442c431db90
- https://git.kernel.org/stable/c/379cae2cb982f571cda9493ac573ab71125fd299
- https://git.kernel.org/stable/c/5d01f2b81568289443d22f1e13a363f829de6343
- https://git.kernel.org/stable/c/656e9a5d69acdd1b20462f4a33378b90ddcb9626
- https://git.kernel.org/stable/c/7500384d3c9587593d75ded3b006835e7aa73ef8
- https://git.kernel.org/stable/c/9c045d4501f7f70724a3bbb561f4f22d292bbfe6
- https://git.kernel.org/stable/c/a29fea30dd93da16652930162b177941abd8c75e
- https://git.kernel.org/stable/c/e516cfd19b0f4c774a57b17fb43a7f41991f0735
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40081.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
