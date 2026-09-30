# [H] CVE-2021-4249

## Summary
Severity: High
Advisory: CVE-2021-4249
Aliases: HSEC-2023-0004
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2021-4249
Type: osv

## Details
A vulnerability was found in xml-conduit. It has been classified as problematic. Affected is an unknown function of the file xml-conduit/src/Text/XML/Stream/Parse.hs of the component DOCTYPE Entity Expansion Handler. The manipulation leads to infinite loop. It is possible to launch the attack remotely. Upgrading to version 1.9.1.0 is able to address this issue. The name of the patch is 4be1021791dcdee8b164d239433a2043dc0939ea. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216204.

## References
- https://hackage.haskell.org/package/xml-conduit-1.9.1.0
- https://vuldb.com/?id.216204
- https://github.com/snoyberg/xml/commit/4be1021791dcdee8b164d239433a2043dc0939ea
- https://github.com/snoyberg/xml/pull/161
