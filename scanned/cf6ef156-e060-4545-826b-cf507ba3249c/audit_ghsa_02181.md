# [M] Unauthorized property update in CheckboxGroup component in Vaadin 12-14 and 15-20

## Summary
Severity: Medium
Advisory: GHSA-qcc4-3rxf-gf4m
CVE: CVE-2021-33605
CWE: CWE-754
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-qcc4-3rxf-gf4m
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-checkbox-flow` — affected >=12.0.0 <14.6.8
- Maven: `com.vaadin:vaadin-checkbox-flow` — affected >=15.0.0 <20.0.6

## Details
Improper check in `CheckboxGroup` in `com.vaadin:vaadin-checkbox-flow` versions 1.2.0 prior to 2.0.0 (Vaadin 12.0.0 prior to 14.0.0), 2.0.0 prior to 3.0.0 (Vaadin 14.0.0 prior to 14.5.0), 3.0.0 through 4.0.1 (Vaadin 15.0.0 through 17.0.11), 14.5.0 through 14.6.7 (Vaadin 14.5.0 through 14.6.7), and 18.0.0 through 20.0.5 (Vaadin 18.0.0 through 20.0.5) allows attackers to modify the value of a disabled `Checkbox` inside enabled `CheckboxGroup` component via unspecified vectors.

- https://vaadin.com/security/cve-2021-33605

## References
- https://github.com/vaadin/flow-components/security/advisories/GHSA-qcc4-3rxf-gf4m
- https://nvd.nist.gov/vuln/detail/CVE-2021-33605
- https://github.com/vaadin/flow-components/pull/1903
- https://github.com/vaadin/flow-components/commit/1aa6bc94c763023bc3fc5849c2a1e8cab3bf6766
- https://github.com/vaadin/flow-components/commit/f136532a735f703f1144f19fee48c9009c659f03
- https://github.com/vaadin/flow-components
- https://vaadin.com/security/cve-2021-33605
