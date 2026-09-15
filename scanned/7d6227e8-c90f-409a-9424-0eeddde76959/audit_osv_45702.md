# [M] JLSEC-2026-23

## Summary
Severity: Medium
Advisory: JLSEC-2026-23
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-23
Type: osv

## Affected
- Julia: `yaml_cpp_jll` — affected >=0 <0.6.3+0

## Details
The SingleDocParser::HandleNode function in yaml-cpp (aka LibYaml-C++) 0.5.3 allows remote attackers to cause a denial of service (stack consumption and application crash) via a crafted YAML file.

## References
- http://seclists.org/fulldisclosure/2024/Nov/0
- http://www.securityfocus.com/bid/97307
- https://github.com/jbeder/yaml-cpp/issues/459
