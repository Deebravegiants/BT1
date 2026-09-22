# [H] CVE-2020-1912

## Summary
Severity: High
Advisory: CVE-2020-1912
Aliases: GHSA-pf27-929j-9pmm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-1912
Type: osv

## Details
An out-of-bounds read/write vulnerability when executing lazily compiled inner generator functions in Facebook Hermes prior to commit 091835377369c8fd5917d9b87acffa721ad2a168 allows attackers to potentially execute arbitrary code via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://www.facebook.com/security/advisories/cve-2020-1912
- https://github.com/facebook/hermes/commit/091835377369c8fd5917d9b87acffa721ad2a168
