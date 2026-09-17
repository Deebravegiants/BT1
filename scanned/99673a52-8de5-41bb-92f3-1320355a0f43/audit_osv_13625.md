# [M] CVE-2018-20574

## Summary
Severity: Medium
Advisory: CVE-2018-20574
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20574
Type: osv

## Details
The SingleDocParser::HandleFlowMap function in yaml-cpp (aka LibYaml-C++) 0.6.2 allows remote attackers to cause a denial of service (stack consumption and application crash) via a crafted YAML file.

## References
- http://seclists.org/fulldisclosure/2024/Nov/0
- https://github.com/jbeder/yaml-cpp/issues/654
