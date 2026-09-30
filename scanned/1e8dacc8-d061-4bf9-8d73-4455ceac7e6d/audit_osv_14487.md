# [H] CVE-2019-10048

## Summary
Severity: High
Advisory: CVE-2019-10048
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-10048
Type: osv

## Details
The ImageMagick plugin that is installed by default in Pydio through 8.2.2 does not perform the appropriate validation and sanitization of user supplied input in the plugin's configuration options, allowing arbitrary shell commands to be entered that result in command execution on the underlying operating system, with the privileges of the local user running the web server. The attacker must be authenticated into the application with an administrator user account in order to be able to edit the affected plugin configuration.

## References
- https://www.secureauth.com/labs/advisories
