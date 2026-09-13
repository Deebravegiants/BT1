# [H] CVE-2021-41040

## Summary
Severity: High
Advisory: CVE-2021-41040
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/CVE-2021-41040
Type: osv

## Details
In Eclipse Wakaama, ever since its inception until 2021-01-14, the CoAP parsing code does not properly sanitize network-received data.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=577968
- https://github.com/eclipse/wakaama/pull/640
