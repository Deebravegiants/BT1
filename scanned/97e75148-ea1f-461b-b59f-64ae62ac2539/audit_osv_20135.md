# [H] CVE-2021-31409

## Summary
Severity: High
Advisory: CVE-2021-31409
Aliases: GHSA-c332-w4jm-55wv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-31409
Type: osv

## Details
Unsafe validation RegEx in EmailValidator component in com.vaadin:vaadin-compatibility-server versions 8.0.0 through 8.12.4 (Vaadin versions 8.0.0 through 8.12.4) allows attackers to cause uncontrolled resource consumption by submitting malicious email addresses.

## References
- https://vaadin.com/security/cve-2021-31409
- https://github.com/vaadin/framework/issues/12240
- https://github.com/vaadin/framework/pull/12241
