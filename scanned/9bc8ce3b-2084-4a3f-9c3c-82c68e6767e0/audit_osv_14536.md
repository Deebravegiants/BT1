# [M] CVE-2019-1010182

## Summary
Severity: Medium
Advisory: CVE-2019-1010182
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-1010182
Type: osv

## Details
yaml-rust 0.4.0 and earlier is affected by: Uncontrolled Recursion. The impact is: Denial of service by impossible to catch abort. The component is: YamlLoader::load_from_str function. The attack vector is: Parsing of a malicious YAML document. The fixed version is: 0.4.1 and later.

## References
- https://github.com/chyh1990/yaml-rust/pull/109
