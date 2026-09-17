# [H] ALPINE-CVE-2026-2474

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-2474
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2474
Type: osv

## Affected
- Alpine:v3.24: `perl-crypt-urandom` — affected >=0.41 <0.55-r0

## Details
Crypt::URandom versions from 0.41 before 0.55 for Perl is vulnerable to a heap buffer overflow in the XS function crypt_urandom_getrandom().

The function does not validate that the length parameter is non-negative. If a negative value (e.g. -1) is supplied, the expression length + 1u causes an integer wraparound, resulting in a zero-byte allocation. The subsequent call to getrandom(data, length, GRND_NONBLOCK) passes the original negative value, which is implicitly converted to a large unsigned value (typically SIZE_MAX). This can result in writes beyond the allocated buffer, leading to heap memory corruption and application crash (denial of service).

In common usage, the length argument is typically hardcoded by the caller, which reduces the likelihood of attacker-controlled exploitation. Applications that pass untrusted input to this parameter may be affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2474
