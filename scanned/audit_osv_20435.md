# [M] CVE-2021-33609

## Summary
Severity: Medium
Advisory: CVE-2021-33609
Aliases: GHSA-qcgx-crrx-38v5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-10-13
Source: https://osv.dev/vulnerability/CVE-2021-33609
Type: osv

## Details
Missing check in DataCommunicator class in com.vaadin:vaadin-server versions 8.0.0 through 8.14.0 (Vaadin 8.0.0 through 8.14.0) allows authenticated network attacker to cause heap exhaustion by requesting too many rows of data.

## References
- https://vaadin.com/security/cve-2021-33609
- https://github.com/vaadin/framework/pull/12415
