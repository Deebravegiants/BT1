# [M] udf: Do not update file length for failed writes to inline files

## Summary
Severity: Medium
Advisory: CVE-2023-53295
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53295
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Do not update file length for failed writes to inline files

When write to inline file fails (or happens only partly), we still
updated length of inline data as if the whole write succeeded. Fix the
update of length of inline data to happen only if the write succeeds.

## References
- https://git.kernel.org/stable/c/256fe4162f8b5a1625b8603ca5f7ff79725bfb47
- https://git.kernel.org/stable/c/5621f7a8139053d0c3c47fb68ee9f602139eb40a
- https://git.kernel.org/stable/c/5a6c373d761f55635e175fa2f407544bae8f583b
- https://git.kernel.org/stable/c/6837910aeb2c9101fc036dcd1b1f32615c20ec1a
- https://git.kernel.org/stable/c/6d18cedc1ef0caeb1567cab660079e48844ff6d6
- https://git.kernel.org/stable/c/7bd8d9e1cf5607ee14407f4060b9a1dbb3c42802
- https://git.kernel.org/stable/c/c5787d77a5c29fffd295d138bd118b334990a567
- https://git.kernel.org/stable/c/eb2133900cac2d2f78befd6be41666cf1a2315d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53295.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53295
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
