# [H] opcua Vulnerable to Out-of-bounds Write

## Summary
Severity: High
Advisory: GHSA-hgxq-hcrm-c5pm
CVE: CVE-2022-25903
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-hgxq-hcrm-c5pm
Type: github-advisory

## Affected
- crates.io: `opcua` — affected >=0 <0.11.0

## Details
The package opcua from 0.0.0 until 0.11.0 is vulnerable to Denial of Service (DoS) via the ExtensionObjects and Variants objects, when it allows unlimited nesting levels, which could result in a stack overflow even if the message size is less than the maximum allowed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25903
- https://github.com/locka99/opcua/pull/216
- https://github.com/locka99/opcua/pull/216/commits/e75dada28a40c3fefc4aeee4cdc272e1b748f8dd
- https://github.com/locka99/opcua
- https://security.snyk.io/vuln/SNYK-RUST-OPCUA-2988750
