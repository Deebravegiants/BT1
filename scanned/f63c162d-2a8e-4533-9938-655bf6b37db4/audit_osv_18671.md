# [C] CVE-2020-35190

## Summary
Severity: Critical
Advisory: CVE-2020-35190
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-17
Source: https://osv.dev/vulnerability/CVE-2020-35190
Type: osv

## Details
The official plone Docker images before version of 4.3.18-alpine (Alpine specific) contain a blank password for a root user. System using the plone docker container deployed by affected versions of the docker image may allow a remote attacker to achieve root access with a blank password.

## References
- https://github.com/koharin/koharin2/blob/main/CVE-2020-35190
