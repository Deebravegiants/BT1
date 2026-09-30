# [M] CVE-2014-8178

## Summary
Severity: Medium
Advisory: CVE-2014-8178
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-12-17
Source: https://osv.dev/vulnerability/CVE-2014-8178
Type: osv

## Details
Docker Engine before 1.8.3 and CS Docker Engine before 1.6.2-CS7 do not use a globally unique identifier to store image layers, which makes it easier for attackers to poison the image cache via a crafted image in pull or push commands.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00014.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00036.html
- https://github.com/docker/docker/blob/master/CHANGELOG.md#183-2015-10-12
- https://www.docker.com/legal/docker-cve-database
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00014.html
- https://groups.google.com/forum/#%21msg/docker-dev/bWVVtLNbFy8/UaefOqMOCAAJ
