# [M] media: s5p_cec: limit msg.len to CEC_MAX_MSG_SIZE

## Summary
Severity: Medium
Advisory: CVE-2022-49035
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-02
Source: https://osv.dev/vulnerability/CVE-2022-49035
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: s5p_cec: limit msg.len to CEC_MAX_MSG_SIZE

I expect that the hardware will have limited this to 16, but just in
case it hasn't, check for this corner case.

## References
- https://git.kernel.org/stable/c/1609231f86760c1f6a429de7913dd795b9faa08c
- https://git.kernel.org/stable/c/2654e785bd4aa2439cdffbe7dc1ea30a0eddbfe4
- https://git.kernel.org/stable/c/4a449430ecfb199b99ba58af63c467eb53500b39
- https://git.kernel.org/stable/c/7ccb40f26cbefa1c6dfd3418bea54c9518cdbd8a
- https://git.kernel.org/stable/c/93f65ce036863893c164ca410938e0968964b26c
- https://git.kernel.org/stable/c/a2728bf9b6c65e46468c763e3dab7e04839d4e11
- https://git.kernel.org/stable/c/cbfa26936f318b16ccf9ca31b8e8b30c0dc087bd
- https://git.kernel.org/stable/c/fc0f76dd5f116fa9291327024dda392f8b4e849c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49035.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49035
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
