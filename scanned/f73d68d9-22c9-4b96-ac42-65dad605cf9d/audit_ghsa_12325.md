# [M] cairo is vulnerable to denial of service due to a null pointer dereference

## Summary
Severity: Medium
Advisory: GHSA-5v3f-73gv-x7x5
CVE: CVE-2017-7475
CWE: CWE-476
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-11-15
Source: https://github.com/advisories/GHSA-5v3f-73gv-x7x5
Type: github-advisory

## Affected
- RubyGems: `cairo` — affected >=1.15.4 <1.15.5

## Details
Cairo version 1.15.4 is vulnerable to a NULL pointer dereference related to the `FT_Load_Glyph` and `FT_Render_Glyph` resulting in an application crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7475
- https://bugs.freedesktop.org/show_bug.cgi?id=100763
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7475
- https://github.com/rcairo/rcairo
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cairo/CVE-2017-7475.yml
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772@%3Cdev.mina.apache.org%3E
- http://seclists.org/oss-sec/2017/q2/151
