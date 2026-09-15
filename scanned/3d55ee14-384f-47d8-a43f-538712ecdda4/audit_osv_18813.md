# [H] CVE-2020-36320

## Summary
Severity: High
Advisory: CVE-2020-36320
Aliases: GHSA-42j4-733x-5vcf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-23
Source: https://osv.dev/vulnerability/CVE-2020-36320
Type: osv

## Details
Unsafe validation RegEx in EmailValidator class in com.vaadin:vaadin-server versions 7.0.0 through 7.7.21 (Vaadin 7.0.0 through 7.7.21) allows attackers to cause uncontrolled resource consumption by submitting malicious email addresses.

## References
- https://vaadin.com/security/cve-2020-36320
- https://github.com/vaadin/framework/issues/7757
- https://github.com/vaadin/framework/pull/12104
