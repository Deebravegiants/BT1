# [M] CVE-2019-1010183

## Summary
Severity: Medium
Advisory: CVE-2019-1010183
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-1010183
Type: osv

## Details
serde serde_yaml 0.6.0 to 0.8.3 is affected by: Uncontrolled Recursion. The impact is: Denial of service by aborting. The component is: from_* functions (all deserialization functions). The attack vector is: Parsing a malicious YAML file. The fixed version is: 0.8.4 and later.

## References
- https://github.com/dtolnay/serde-yaml/pull/105
