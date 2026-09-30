# [C] openDCIM <= 23.04 Missing Authorization in install.php

## Summary
Severity: Critical
Advisory: CVE-2026-28515
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28515
Type: osv

## Details
openDCIM version 23.04, through commit 4467e9c4, contains a missing authorization vulnerability in install.php and container-install.php. The installer and upgrade handler expose LDAP configuration functionality without enforcing application role checks. Any authenticated user can access this functionality regardless of assigned privileges. In deployments where REMOTE_USER is set without authentication enforcement, the endpoint may be accessible without credentials. This allows unauthorized modification of application configuration.

## References
- https://github.com/opendcim/openDCIM/blob/4467e9c4/container-install.php#L421-L435
- https://github.com/opendcim/openDCIM/blob/4467e9c4/install.php#L293
- https://github.com/opendcim/openDCIM/blob/4467e9c4/install.php#L420-L434
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28515.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28515
- https://www.vulncheck.com/advisories/opendcim-missing-authorization-in-install-php
- https://github.com/opendcim/openDCIM/pull/1664
- https://github.com/opendcim/openDCIM/pull/1664/changes/8f7ab2a710086a9c8c269560793e47c577ddda09
- https://github.com/opendcim/openDCIM
- https://chocapikk.com/posts/2026/opendcim-sqli-to-rce/
- https://github.com/Chocapikk/opendcim-exploit
