# [H] firmware: arm_scmi: Fix list protocols enumeration in the base protocol

## Summary
Severity: High
Advisory: CVE-2022-49451
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49451
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_scmi: Fix list protocols enumeration in the base protocol

While enumerating protocols implemented by the SCMI platform using
BASE_DISCOVER_LIST_PROTOCOLS, the number of returned protocols is
currently validated in an improper way since the check employs a sum
between unsigned integers that could overflow and cause the check itself
to be silently bypassed if the returned value 'loop_num_ret' is big
enough.

Fix the validation avoiding the addition.

## References
- https://git.kernel.org/stable/c/1052f22e127d0c34c3387bb389424ba1c61491ff
- https://git.kernel.org/stable/c/2ccfcd7a09c826516edcfe464b05071961aada3f
- https://git.kernel.org/stable/c/444a2d27fe9867d0da4b28fc45b793f32e099ab8
- https://git.kernel.org/stable/c/6e7978695f4a6cbd83616b5a702b77fa2087b247
- https://git.kernel.org/stable/c/8009120e0354a67068e920eb10dce532391361d0
- https://git.kernel.org/stable/c/98342148a8cd242855d7e257f298c966c96dba9f
- https://git.kernel.org/stable/c/b0e4bafac8963c2d85ee18d3d01f393735acceec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49451.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49451
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
