# [C] CVE-2021-32642

## Summary
Severity: Critical
Advisory: CVE-2021-32642
Aliases: GHSA-56gw-9rj9-55rc
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-32642
Type: osv

## Details
radsecproxy is a generic RADIUS proxy that supports both UDP and TLS (RadSec) RADIUS transports. Missing input validation in radsecproxy's `naptr-eduroam.sh` and `radsec-dynsrv.sh` scripts can lead to configuration injection via crafted radsec peer discovery DNS records. Users are subject to Information disclosure, Denial of Service, Redirection of Radius connection to a non-authenticated server leading to non-authenticated network access. Updated example scripts are available in the master branch and 1.9 release. Note that the scripts are not part of the installation package and are not updated automatically. If you are using the examples, you have to update them manually. The dyndisc scripts work independently of the radsecproxy code. The updated scripts can be used with any version of radsecproxy.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HOC5AFG65NYLMMUTNSBOPC5F4LBAC7BR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W7QK5M2SZVMCAFSRQMM6PRZZRQQ372XI/
- https://github.com/radsecproxy/radsecproxy/security/advisories/GHSA-56gw-9rj9-55rc
- https://www.usenix.org/conference/usenixsecurity21/presentation/jeitner
