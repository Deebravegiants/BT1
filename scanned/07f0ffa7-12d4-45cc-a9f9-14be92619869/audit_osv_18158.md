# [H] CVE-2020-24621

## Summary
Severity: High
Advisory: CVE-2020-24621
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-25
Source: https://osv.dev/vulnerability/CVE-2020-24621
Type: osv

## Details
A remote code execution (RCE) vulnerability was discovered in the htmlformentry (aka HTML Form Entry) module before 3.11.0 for OpenMRS. By leveraging path traversal, a malicious Velocity Template Language file could be written to a directory. This file could then be accessed and executed.

## References
- https://issues.openmrs.org/browse/HTML-730
- https://www.contrastsecurity.com/security-influencers
- https://github.com/openmrs/openmrs-module-htmlformentry/pull/178
- https://github.com/openmrs/openmrs-module-uiframework/pull/59
- https://www.contrastsecurity.com/security-influencers/authenticated-remote-code-execution-openmrs
