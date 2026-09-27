# [M] CVE-2018-25007

## Summary
Severity: Medium
Advisory: CVE-2018-25007
Aliases: GHSA-jmx8-355m-8vwh
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-04-23
Source: https://osv.dev/vulnerability/CVE-2018-25007
Type: osv

## Details
Missing check in UIDL request handler in com.vaadin:flow-server versions 1.0.0 through 1.0.5 (Vaadin 10.0.0 through 10.0.7, and 11.0.0 through 11.0.2) allows attacker to update element property values via crafted synchronization message.

## References
- https://vaadin.com/security/cve-2018-25007
- https://github.com/vaadin/flow/pull/4774
