# [C] CVE-2021-33473

## Summary
Severity: Critical
Advisory: CVE-2021-33473
Aliases: GHSA-fj34-jhjx-xmvv
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2021-33473
Type: osv

## Details
An argument injection vulnerability in Dragonfly Ruby Gem v1.3.0 allows attackers to read and write arbitrary files when the verify_url option is disabled. This vulnerability is exploited via a crafted URL.

## References
- https://security.netapp.com/advisory/ntap-20220715-0004/
- https://github.com/markevans/dragonfly/issues/513
- https://github.com/markevans/dragonfly/commit/25399297bb457f7fcf8e3f91e85945b255b111b5
