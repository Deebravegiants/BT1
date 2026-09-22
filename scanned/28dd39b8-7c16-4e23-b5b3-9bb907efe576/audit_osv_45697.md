# [H] JLSEC-2026-22

## Summary
Severity: High
Advisory: JLSEC-2026-22
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-22
Type: osv

## Affected
- Julia: `yaml_cpp_jll` — affected >=0 <0.6.3+0

## Details
The function "Token& Scanner::peek" in scanner.cpp in yaml-cpp 0.5.3 and earlier allows remote attackers to cause a denial of service (assertion failure and application exit) via a '!2' string.

## References
- https://github.com/jbeder/yaml-cpp/issues/519
- https://security.gentoo.org/glsa/202007-14
