# [M] CVE-2021-21400

## Summary
Severity: Medium
Advisory: CVE-2021-21400
Aliases: GHSA-cxwr-f2j3-q8hp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-04-02
Source: https://osv.dev/vulnerability/CVE-2021-21400
Type: osv

## Details
wire-webapp is an open-source front end for Wire, a secure collaboration platform. In wire-webapp before version 2021-03-15-production.0, when being prompted to enter the app-lock passphrase, the typed passphrase will be sent into the most recently used chat when the user does not actively give focus to the input field. Input element focus is enforced programatically in version 2021-03-15-production.0.

## References
- https://github.com/wireapp/wire-webapp/releases/tag/2021-03-15-production.0
- https://github.com/wireapp/wire-webapp/security/advisories/GHSA-cxwr-f2j3-q8hp
- https://github.com/wireapp/wire-webapp/commit/281f2a9d795f68abe423c116d5da4e1e73a60062
- https://github.com/wireapp/wire-webapp/pull/10704
