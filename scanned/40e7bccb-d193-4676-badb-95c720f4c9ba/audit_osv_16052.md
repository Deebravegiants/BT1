# [H] CVE-2019-25102

## Summary
Severity: High
Advisory: CVE-2019-25102
Aliases: GHSA-j533-2g8v-pmpg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-12
Source: https://osv.dev/vulnerability/CVE-2019-25102
Type: osv

## Details
A vulnerability, which was classified as problematic, was found in simple-markdown 0.6.0. Affected is an unknown function of the file simple-markdown.js. The manipulation with the input <<<<<<<<<<:/:/:/:/:/:/:/:/:/:/ leads to inefficient regular expression complexity. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 0.6.1 is able to address this issue. The patch is identified as 015a719bf5cdc561feea05500ecb3274ef609cd2. It is recommended to upgrade the affected component. VDB-220638 is the identifier assigned to this vulnerability.

## References
- https://github.com/ariabuckles/simple-markdown/releases/tag/0.6.1
- https://vuldb.com/?ctiid.220638
- https://vuldb.com/?id.220638
- https://github.com/ariabuckles/simple-markdown/commit/015a719bf5cdc561feea05500ecb3274ef609cd2
- https://github.com/ariabuckles/simple-markdown/pull/73
