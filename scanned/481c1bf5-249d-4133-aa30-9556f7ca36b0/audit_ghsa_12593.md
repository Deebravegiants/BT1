# [M] Kredis JSON Possible Deserialization of Untrusted Data Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h2wm-p2vg-6pw4
CVE: CVE-2023-27531
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-h2wm-p2vg-6pw4
Type: github-advisory

## Affected
- RubyGems: `kredis` — affected >=0 <1.3.0.1

## Details
There is a deserialization of untrusted data vulnerability in
the Kredis JSON deserialization code. This vulnerability has
been assigned the CVE identifier CVE-2023-27531.

'Not affected: None.'
'Versions Affected: All.'
'Fixed Versions: 1.3.0.1'

Impact
  Carefully crafted JSON data processed by Kredis may result in
  deserialization of untrusted data, potentially leading to
  deserialization of unexpected objects in the system.

  Any applications using Kredis with JSON are affected.

Releases
  The fixed releases are available at the normal locations.

Workarounds
  There are no feasible workarounds for this issue.

Patches
  To aid users who aren’t able to upgrade immediately we have
  provided patches for the two supported release series. They
  are in git-am format and consist of a single changeset.

  * 1-3-0-1-kredis.patch - Patch for 1.3.0 series

Credits
  Thank you ooooooo_k 7 for reporting this!

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27531
- https://github.com/rails/kredis/commit/d576b7ae5c8d3d74eeb4bd84cad0aa64ffc299fa
- https://discuss.rubyonrails.org/t/cve-2023-27531-possible-deserialization-of-untrusted-data-vulnerability-in-kredis-json/82467
- https://discuss.rubyonrails.org/t/cve-2023-27531-possible-deserialization-of-untrusted-data-vulnerability-in-kredis-json/82467#post_1
- https://github.com/rails/kredis
- https://github.com/rails/kredis/releases/tag/v1.3.0.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kredis/CVE-2023-27531.yml
