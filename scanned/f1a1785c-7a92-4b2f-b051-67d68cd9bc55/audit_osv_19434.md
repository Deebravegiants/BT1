# [H] CVE-2021-21306

## Summary
Severity: High
Advisory: CVE-2021-21306
Aliases: GHSA-4r62-v4vq-hr96
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-21306
Type: osv

## Details
Marked is an open-source markdown parser and compiler (npm package "marked"). In marked from version 1.1.1 and before version 2.0.0, there is a Regular expression Denial of Service vulnerability. This vulnerability can affect anyone who runs user generated code through marked. This vulnerability is fixed in version 2.0.0.

## References
- https://github.com/markedjs/marked/issues/1927
- https://github.com/markedjs/marked/security/advisories/GHSA-4r62-v4vq-hr96
- https://www.npmjs.com/package/marked
- https://github.com/markedjs/marked/commit/7293251c438e3ee968970f7609f1a27f9007bccd
- https://github.com/markedjs/marked/pull/1864
