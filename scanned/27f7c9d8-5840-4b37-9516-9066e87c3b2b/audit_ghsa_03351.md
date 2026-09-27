# [M] Timing side channel vulnerability in endpoint request handler in Vaadin 15-19

## Summary
Severity: Medium
Advisory: GHSA-p7jq-v8jp-j424
CVE: CVE-2021-31406
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-p7jq-v8jp-j424
Type: github-advisory

## Affected
- Maven: `com.vaadin:flow-server` — affected >=3.0.0 <5.0.4
- Maven: `com.vaadin:flow-server` — affected >=6.0.0 <6.0.1

## Details
Non-constant-time comparison of CSRF tokens in endpoint request handler in `com.vaadin:flow-server` versions 3.0.0 through 5.0.3 (Vaadin 15.0.0 through 18.0.6), and com.vaadin:fusion-endpoint version 6.0.0 (Vaadin 19.0.0) allows attacker to guess a security token for Fusion endpoints via timing attack.

- https://vaadin.com/security/cve-2021-31406

## References
- https://github.com/vaadin/flow/security/advisories/GHSA-p7jq-v8jp-j424
- https://nvd.nist.gov/vuln/detail/CVE-2021-31406
- https://github.com/vaadin/flow/pull/10157
- https://vaadin.com/security/cve-2021-31406
