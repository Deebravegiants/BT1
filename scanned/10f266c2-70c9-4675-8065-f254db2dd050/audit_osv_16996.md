# [H] CVE-2020-11061

## Summary
Severity: High
Advisory: CVE-2020-11061
Aliases: GHSA-mm45-cg35-54j4
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-07-10
Source: https://osv.dev/vulnerability/CVE-2020-11061
Type: osv

## Details
In Bareos Director less than or equal to 16.2.10, 17.2.9, 18.2.8, and 19.2.7, a heap overflow allows a malicious client to corrupt the director's memory via oversized digest strings sent during initialization of a verify job. Disabling verify jobs mitigates the problem. This issue is also patched in Bareos versions 19.2.8, 18.2.9 and 17.2.10.

## References
- https://bugs.bareos.org/view.php?id=1210
- https://github.com/bareos/bareos/security/advisories/GHSA-mm45-cg35-54j4
- https://lists.debian.org/debian-lts-announce/2020/08/msg00051.html
