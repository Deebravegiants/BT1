# [M] CVE-2017-5950

## Summary
Severity: Medium
Advisory: CVE-2017-5950
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-5950
Type: osv

## Details
The SingleDocParser::HandleNode function in yaml-cpp (aka LibYaml-C++) 0.5.3 allows remote attackers to cause a denial of service (stack consumption and application crash) via a crafted YAML file.

## References
- http://seclists.org/fulldisclosure/2024/Nov/0
- http://www.securityfocus.com/bid/97307
- https://github.com/jbeder/yaml-cpp/issues/459
