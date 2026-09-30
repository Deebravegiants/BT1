# [C] CVE-2020-29591

## Summary
Severity: Critical
Advisory: CVE-2020-29591
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-29591
Type: osv

## Details
Versions of the Official registry Docker images through 2.7.0 contain a blank password for the root user. Systems deployed using affected versions of the registry container may allow a remote attacker to achieve root access with a blank password.

## References
- https://hub.docker.com/_/registry
- https://github.com/donghyunlee00/CVE/blob/main/CVE-2020-29591
- https://github.com/docker/distribution-library-image
