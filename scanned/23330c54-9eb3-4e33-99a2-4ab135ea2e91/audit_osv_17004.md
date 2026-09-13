# [C] CVE-2020-11079

## Summary
Severity: Critical
Advisory: CVE-2020-11079
Aliases: GHSA-wh69-wc6q-7888
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-28
Source: https://osv.dev/vulnerability/CVE-2020-11079
Type: osv

## Details
node-dns-sync (npm module dns-sync) through 0.2.0 allows execution of arbitrary commands . This issue may lead to remote code execution if a client of the library calls the vulnerable method with untrusted input. This has been fixed in 0.2.1.

## References
- https://github.com/skoranga/node-dns-sync/security/advisories/GHSA-wh69-wc6q-7888
- https://github.com/skoranga/node-dns-sync/commit/cb10a5ac7913eacc031ade7d91596277f31645dc
