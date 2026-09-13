# [M] CVE-2023-6135

## Summary
Severity: Medium
Advisory: CVE-2023-6135
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6135
Type: osv

## Details
Multiple NSS NIST curves were susceptible to a side-channel attack known as "Minerva". This attack could potentially allow an attacker to recover the private key. This vulnerability affects Firefox < 121.

## References
- https://security.gentoo.org/glsa/202401-10
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1853908
