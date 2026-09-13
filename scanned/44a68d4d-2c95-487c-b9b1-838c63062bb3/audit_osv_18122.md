# [C] CVE-2020-24264

## Summary
Severity: Critical
Advisory: CVE-2020-24264
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-16
Source: https://osv.dev/vulnerability/CVE-2020-24264
Type: osv

## Details
Portainer 1.24.1 and earlier is affected by incorrect access control that may lead to remote arbitrary code execution. The restriction checks for bind mounts are applied only on the client-side and not the server-side, which can lead to spawning a container with bind mount. Once such a container is spawned, it can be leveraged to break out of the container leading to complete Docker host machine takeover.

## References
- https://github.com/portainer/portainer/issues/4106
