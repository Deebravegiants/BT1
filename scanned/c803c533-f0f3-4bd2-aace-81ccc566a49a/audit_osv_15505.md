# [C] CVE-2019-16915

## Summary
Severity: Critical
Advisory: CVE-2019-16915
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2019-16915
Type: osv

## Details
An issue was discovered in pfSense through 2.4.4-p3. widgets/widgets/picture.widget.php uses the widgetkey parameter directly without sanitization (e.g., a basename call) for a pathname to file_get_contents or file_put_contents.

## References
- https://www.seebug.org/vuldb/ssvid-98024
- https://redmine.pfsense.org/issues/9610
- https://github.com/pfsense/pfsense/commit/2c544ac61ce98f716d50b8e5961d7dfba66804b5
