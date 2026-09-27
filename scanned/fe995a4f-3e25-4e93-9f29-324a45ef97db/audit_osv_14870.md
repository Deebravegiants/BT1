# [H] CVE-2019-12105

## Summary
Severity: High
Advisory: CVE-2019-12105
Aliases: PYSEC-2019-126
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2019-09-10
Source: https://osv.dev/vulnerability/CVE-2019-12105
Type: osv

## Details
In Supervisor through 4.0.2, an unauthenticated user can read log files or restart a service. Note: The maintainer responded that the affected component, inet_http_server, is not enabled by default but if the user enables it and does not set a password, Supervisor logs a warning message. The maintainer indicated the ability to run an open server will not be removed but an additional warning was added to the documentation

## References
- http://supervisord.org/configuration.html#inet-http-server-section-settings
- https://github.com/Supervisor/supervisor/issues/1245
- https://github.com/Supervisor/supervisor/commit/4e334d9cf2a1daff685893e35e72398437df3dcb
