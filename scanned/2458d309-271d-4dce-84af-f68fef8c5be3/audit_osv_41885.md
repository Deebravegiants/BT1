# [H] ASoC: codecs: fs210x: fix possible buffer overflow

## Summary
Severity: High
Advisory: CVE-2026-64041
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64041
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: fs210x: fix possible buffer overflow

In fs210x_effect_scene_info(), a string was copied like this:

    strscpy(DST, SRC, strlen(SRC) + 1);

A buffer overflow would happen if strlen(SRC) >= sizeof(DST).
Actually, strscpy() must be used this way:

    strscpy(DST, SRC, sizeof(DST));
    strscpy(DST, SRC); // defaults to sizeof(DST)

## References
- https://git.kernel.org/stable/c/0d435a7ebcd4e97e47673c1ab6fb27f973a053ec
- https://git.kernel.org/stable/c/1ddf678bb75b6383c775ece61d40956c441d8a26
- https://git.kernel.org/stable/c/6daefdf1cd3c56483f61970a76c0ad6028e4118f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64041.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64041
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
