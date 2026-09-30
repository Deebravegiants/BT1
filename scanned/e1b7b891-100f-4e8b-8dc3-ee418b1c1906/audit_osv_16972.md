# [M] CVE-2020-11006

## Summary
Severity: Medium
Advisory: CVE-2020-11006
Aliases: GHSA-8pc4-gvfw-634p
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-05-08
Source: https://osv.dev/vulnerability/CVE-2020-11006
Type: osv

## Details
In Shopizer before version 2.11.0, a script can be injected in various forms and saved in the database, then executed when information is fetched from backend. This has been patched in version 2.11.0.

## References
- https://github.com/shopizer-ecommerce/shopizer/security/advisories/GHSA-8pc4-gvfw-634p
- https://github.com/shopizer-ecommerce/shopizer/commit/929ca0839a80c6f4dad087e0259089908787ad2a
