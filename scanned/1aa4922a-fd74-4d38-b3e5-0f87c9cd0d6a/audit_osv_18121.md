# [H] CVE-2020-24263

## Summary
Severity: High
Advisory: CVE-2020-24263
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-16
Source: https://osv.dev/vulnerability/CVE-2020-24263
Type: osv

## Details
Portainer 1.24.1 and earlier is affected by an insecure permissions vulnerability that may lead to remote arbitrary code execution. A non-admin user is allowed to spawn new containers with critical capabilities such as SYS_MODULE, which can be used to take over the Docker host.

## References
- https://github.com/portainer/portainer/issues/4105
