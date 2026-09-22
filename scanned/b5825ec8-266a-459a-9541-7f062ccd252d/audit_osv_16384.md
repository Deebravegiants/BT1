# [M] CVE-2019-6292

## Summary
Severity: Medium
Advisory: CVE-2019-6292
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2019-6292
Type: osv

## Details
An issue was discovered in singledocparser.cpp in yaml-cpp (aka LibYaml-C++) 0.6.2. Stack Exhaustion occurs in YAML::SingleDocParser, and there is a stack consumption problem caused by recursive stack frames: HandleCompactMap, HandleMap, HandleFlowSequence, HandleSequence, HandleNode. Remote attackers could leverage this vulnerability to cause a denial-of-service via a cpp file.

## References
- https://github.com/jbeder/yaml-cpp/issues/657
