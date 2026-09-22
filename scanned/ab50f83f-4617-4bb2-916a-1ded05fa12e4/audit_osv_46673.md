# [H] CVE-2014-8179

## Summary
Severity: High
Advisory: CVE-2014-8179
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-12-17
Source: https://osv.dev/vulnerability/CVE-2014-8179
Type: osv

## Details
Docker Engine before 1.8.3 and CS Docker Engine before 1.6.2-CS7 does not properly validate and extract the manifest object from its JSON representation during a pull, which allows attackers to inject new attributes in a JSON object and bypass pull-by-digest validation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00014.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00036.html
- https://blog.docker.com/2015/10/security-release-docker-1-8-3-1-6-2-cs7/
- https://github.com/docker/docker/blob/master/CHANGELOG.md#183-2015-10-12
- https://www.docker.com/legal/docker-cve-database
- https://blog.docker.com/2015/10/security-release-docker-1-8-3-1-6-2-cs7/
- https://groups.google.com/forum/#%21msg/docker-dev/bWVVtLNbFy8/UaefOqMOCAAJ
