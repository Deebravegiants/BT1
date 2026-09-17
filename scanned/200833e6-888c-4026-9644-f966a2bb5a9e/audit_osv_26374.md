# [H] ALSA: hda/via: Avoid potential array out-of-bound in add_secret_dac_path()

## Summary
Severity: High
Advisory: CVE-2023-52988
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52988
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <4.14.306, >=4.15.0 <4.19.273, >=4.20.0 <5.4.232, >=5.5.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda/via: Avoid potential array out-of-bound in add_secret_dac_path()

snd_hda_get_connections() can return a negative error code.
It may lead to accessing 'conn' array at a negative index.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/1b9256c96220bcdba287eeeb90e7c910c77f8c46
- https://git.kernel.org/stable/c/2b557fa635e7487f638c0f030c305870839eeda2
- https://git.kernel.org/stable/c/437e50ef6290ac835d526d0e45f466a0aa69ba1b
- https://git.kernel.org/stable/c/6e1f586ddec48d71016b81acf68ba9f49ca54db8
- https://git.kernel.org/stable/c/b9cee506da2b7920b5ea02ccd8e78a907d0ee7aa
- https://git.kernel.org/stable/c/d6870f3800dbb212ae8433183ee82f566d067c6c
- https://git.kernel.org/stable/c/f011360ad234a07cb6fbcc720fff646a93a9f0d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52988.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
