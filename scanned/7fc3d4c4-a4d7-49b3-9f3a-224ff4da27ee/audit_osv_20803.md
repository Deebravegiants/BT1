# [C] CVE-2021-37232

## Summary
Severity: Critical
Advisory: CVE-2021-37232
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2021-37232
Type: osv

## Details
A stack overflow vulnerability occurs in Atomicparsley 20210124.204813.840499f through APar_read64() in src/util.cpp due to the lack of buffer size of uint32_buffer while reading more bytes in APar_read64.

## References
- https://security.gentoo.org/glsa/202305-01
- https://github.com/wez/atomicparsley/commit/d72ccf06c98259d7261e0f3ac4fd8717778782c1
- https://github.com/wez/atomicparsley/issues/32
