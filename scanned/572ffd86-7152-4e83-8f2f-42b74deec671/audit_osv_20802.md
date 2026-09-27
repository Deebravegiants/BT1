# [M] CVE-2021-37231

## Summary
Severity: Medium
Advisory: CVE-2021-37231
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2021-37231
Type: osv

## Details
A stack-buffer-overflow occurs in Atomicparsley 20210124.204813.840499f through APar_readX() in src/util.cpp while parsing a crafted mp4 file because of the missing boundary check.

## References
- https://github.com/wez/atomicparsley/pull/31#issue-687280335
- https://security.gentoo.org/glsa/202305-01
- https://github.com/wez/atomicparsley/issues/30
