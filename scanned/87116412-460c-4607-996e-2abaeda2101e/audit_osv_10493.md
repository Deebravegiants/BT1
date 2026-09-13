# [H] CVE-2017-16540

## Summary
Severity: High
Advisory: CVE-2017-16540
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16540
Type: osv

## Details
OpenEMR before 5.0.0 Patch 5 allows unauthenticated remote database copying because setup.php exposes functionality for cloning an existing OpenEMR site to an arbitrary attacker-controlled MySQL server via vectors involving a crafted state parameter.

## References
- http://www.securityfocus.com/bid/101983
- https://isears.github.io/jekyll/update/2017/10/28/openemr-database-disclosure.html
- http://www.open-emr.org/wiki/index.php/OpenEMR_Patches
