# [M] Nokogiri updates packaged libxml2 to v2.10.4 to resolve multiple CVEs

## Summary
Severity: Medium
Advisory: GHSA-pxvg-2qj5-37jq
Ecosystem: RubyGems
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-pxvg-2qj5-37jq
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.14.3

## Details
### Summary

Nokogiri v1.14.3 upgrades the packaged version of its dependency libxml2 to [v2.10.4](https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.10.4) from v2.10.3.

libxml2 v2.10.4 addresses the following known vulnerabilities:

- [CVE-2023-29469](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-29469): Hashing of empty dict strings isn't deterministic
- [CVE-2023-28484](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-28484): Fix null deref in xmlSchemaFixupComplexType
- Schemas: Fix null-pointer-deref in xmlSchemaCheckCOSSTDerivedOK

Please note that this advisory only applies to the CRuby implementation of Nokogiri `< 1.14.3`, and only if the _packaged_ libraries are being used. If you've overridden defaults at installation time to use _system_ libraries instead of packaged libraries, you should instead pay attention to your distro's `libxml2` release announcements.


### Mitigation

Upgrade to Nokogiri `>= 1.14.3`.

Users who are unable to upgrade Nokogiri may also choose a more complicated mitigation: compile and link Nokogiri against external libraries libxml2 `>= 2.10.4` which will also address these same issues.


### Impact

No public information has yet been published about the security-related issues other than the upstream commits. Examination of those changesets indicate that the more serious issues relate to libxml2 dereferencing NULL pointers and potentially segfaulting while parsing untrusted inputs.

The commits can be examined at:

- [[CVE-2023-29469] Hashing of empty dict strings isn't deterministic (09a2dd45) · Commits · GNOME / libxml2 · GitLab](https://gitlab.gnome.org/GNOME/libxml2/-/commit/09a2dd453007f9c7205274623acdd73747c22d64)
- [[CVE-2023-28484] Fix null deref in xmlSchemaFixupComplexType (647e072e) · Commits · GNOME / libxml2 · GitLab](https://gitlab.gnome.org/GNOME/libxml2/-/commit/647e072ea0a2f12687fa05c172f4c4713fdb0c4f)
- [schemas: Fix null-pointer-deref in xmlSchemaCheckCOSSTDerivedOK (4c6922f7) · Commits · GNOME / libxml2 · GitLab](https://gitlab.gnome.org/GNOME/libxml2/-/commit/4c6922f763ad958c48ff66f82823ae21f2e92ee6)

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-pxvg-2qj5-37jq
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-28484
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-29469
- https://github.com/sparklemotion/nokogiri
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/09a2dd453007f9c7205274623acdd73747c22d64
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/4c6922f763ad958c48ff66f82823ae21f2e92ee6
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/647e072ea0a2f12687fa05c172f4c4713fdb0c4f
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.10.4
