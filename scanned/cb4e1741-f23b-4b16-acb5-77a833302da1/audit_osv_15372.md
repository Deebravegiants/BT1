# [M] CVE-2019-15700

## Summary
Severity: Medium
Advisory: CVE-2019-15700
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-08-27
Source: https://osv.dev/vulnerability/CVE-2019-15700
Type: osv

## Details
public/js/frappe/form/footer/timeline.js in Frappe Framework 12 through 12.0.8 does not escape HTML in the timeline and thus is affected by crafted "changed value of" text.

## References
- https://github.com/frappe/frappe/pull/8262
