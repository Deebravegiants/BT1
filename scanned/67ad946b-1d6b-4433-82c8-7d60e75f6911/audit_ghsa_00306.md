# [C] Unsafe deserialization in confire

## Summary
Severity: Critical
Advisory: GHSA-m85c-9mf8-m2m6
CVE: CVE-2017-16763
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-m85c-9mf8-m2m6
Type: github-advisory

## Affected
- PyPI: `confire` — affected >=0

## Details
An exploitable vulnerability exists in the YAML parsing functionality in config.py in Confire 0.2.0. Due to the user-specific configuration being loaded from "~/.confire.yaml" using the yaml.load function, a YAML parser can execute arbitrary Python commands resulting in command execution. An attacker can insert Python into loaded YAML to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16763
- https://github.com/bbengfort/confire/issues/24
- https://github.com/bbengfort/confire/commit/8cc86a5ec2327e070f1d576d61bbaadf861597ea
- https://github.com/advisories/GHSA-m85c-9mf8-m2m6
- https://github.com/bbengfort/confire
- https://github.com/pypa/advisory-database/tree/main/vulns/confire/PYSEC-2017-78.yaml
- https://joel-malwarebenchmark.github.io/blog/2017/11/12/cve-2017-16763-configure-loaded-through-confire
