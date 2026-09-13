# [M] Nokogiri update packaged libxml2 to v2.12.5 to resolve CVE-2024-25062

## Summary
Severity: Medium
Advisory: GHSA-xc9x-jj77-9p9j
CWE: CWE-416
Ecosystem: RubyGems
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-xc9x-jj77-9p9j
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.16.0 <1.16.2
- RubyGems: `nokogiri` — affected >=0 <1.15.6

## Details
## Summary

Nokogiri upgrades its dependency libxml2 as follows:
- Nokogiri v1.15.6 upgrades libxml2 to [2.11.7](https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.11.7) from 2.11.6
- Nokogiri v1.16.2 upgrades libxml2 to [2.12.5](https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.12.5) from 2.12.4

libxml2 v2.11.7 and v2.12.5 address the following vulnerability:

- CVE-2024-25062 / https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-25062
  - described at https://gitlab.gnome.org/GNOME/libxml2/-/issues/604
  - patched by https://gitlab.gnome.org/GNOME/libxml2/-/commit/92721970

Please note that this advisory only applies to the CRuby implementation of Nokogiri, and only if the _packaged_ libraries are being used. If you've overridden defaults at installation time to use _system_ libraries instead of packaged libraries, you should instead pay attention to your distro's `libxml2` release announcements.

JRuby users are not affected.

## Mitigation

Upgrade to Nokogiri `~> 1.15.6` or `>= 1.16.2`.

Users who are unable to upgrade Nokogiri may also choose a more complicated mitigation: compile
and link Nokogiri against patched external libxml2 libraries which will also address these same
issues.

## Impact

From the CVE description, this issue applies to the `xmlTextReader` module (which underlies `Nokogiri::XML::Reader`):

> When using the XML Reader interface with DTD validation and XInclude expansion enabled, processing crafted XML documents can lead to an xmlValidatePopElement use-after-free.

## Timeline

- 2024-02-04 10:35 EST - this GHSA is drafted without complete details about when the upstream issue was introduced; a request is made of libxml2 maintainers for more detailed information
- 2024-02-04 10:48 EST - updated GHSA to reflect libxml2 maintainers' confirmation of affected versions
- 2024-02-04 11:54 EST - v1.16.2 published, this GHSA made public
- 2024-02-05 10:18 EST - updated with MITRE link to the CVE information, and updated "Impact" section
- 2024-03-16 09:03 EDT - v1.15.6 published (see discussion at https://github.com/sparklemotion/nokogiri/discussions/3146), updated mitigation information
- 2024-03-18 22:12 EDT - update "affected products" range with v1.15.6 information

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-xc9x-jj77-9p9j
- https://nvd.nist.gov/vuln/detail/CVE-2024-25062
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/GHSA-xc9x-jj77-9p9j.yml
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/discussions/3146
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/92721970
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/604
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.12.5
