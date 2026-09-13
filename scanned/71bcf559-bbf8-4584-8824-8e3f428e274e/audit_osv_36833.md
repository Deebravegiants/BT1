# [H] Crypt::SysRandom::XS versions before 0.010 for Perl is vulnerable to a heap buffer overflow in the XS function random_bytes()

## Summary
Severity: High
Advisory: CVE-2026-2597
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-2597
Type: osv

## Details
Crypt::SysRandom::XS versions before 0.010 for Perl is vulnerable to a heap buffer overflow in the XS function random_bytes().

The function does not validate that the length parameter is non-negative. If a negative value (e.g. -1) is supplied, the expression length + 1u causes an integer wraparound, resulting in a zero-byte allocation. The subsequent call to chosen random function (e.g. getrandom) passes the original negative value, which is implicitly converted to a large unsigned value (typically SIZE_MAX). This can result in writes beyond the allocated buffer, leading to heap memory corruption and application crash (denial of service).

In common usage, the length argument is typically hardcoded by the caller, which reduces the likelihood of attacker-controlled exploitation. Applications that pass untrusted input to this parameter may be affected.

## References
- https://cpan.org/modules
- https://metacpan.org/release/LEONT/Crypt-SysRandom-XS-0.011/source/lib/Crypt/SysRandom/XS.xs#L51-52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2597.json
- https://metacpan.org/dist/Crypt-SysRandom-XS/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-2597
- https://github.com/Leont/crypt-sysrandom-xs
