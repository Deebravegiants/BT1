# [M] CVE-2019-6285

## Summary
Severity: Medium
Advisory: CVE-2019-6285
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-14
Source: https://osv.dev/vulnerability/CVE-2019-6285
Type: osv

## Details
The SingleDocParser::HandleFlowSequence function in yaml-cpp (aka LibYaml-C++) 0.6.2 allows remote attackers to cause a denial of service (stack consumption and application crash) via a crafted YAML file.

## References
- http://seclists.org/fulldisclosure/2024/Nov/0
- https://github.com/jbeder/yaml-cpp/issues/660
