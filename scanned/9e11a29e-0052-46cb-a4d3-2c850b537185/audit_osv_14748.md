# [H] CVE-2019-11270

## Summary
Severity: High
Advisory: CVE-2019-11270
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-08-05
Source: https://osv.dev/vulnerability/CVE-2019-11270
Type: osv

## Details
Cloud Foundry UAA versions prior to v73.4.0 contain a vulnerability where a malicious client possessing the 'clients.write' authority or scope can bypass the restrictions imposed on clients created via 'clients.write' and create clients with arbitrary scopes that the creator does not possess.

## References
- https://pivotal.io/security/cve-2019-11270
- https://www.cloudfoundry.org/blog/cve-2019-11270
