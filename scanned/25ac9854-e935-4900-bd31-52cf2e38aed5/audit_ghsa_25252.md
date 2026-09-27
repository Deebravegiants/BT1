# [M] RubyGems file overwrite vulnerability

## Summary
Severity: Medium
Advisory: GHSA-95vx-q4c2-64gr
CVE: CVE-2007-0469
Ecosystem: RubyGems
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-95vx-q4c2-64gr
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <0.9.1

## Details
The `extract_files` function in `installer.rb` in RubyGems before 0.9.1 does not check whether files exist before overwriting them, which allows user-assisted remote attackers to overwrite arbitrary files, cause a denial of service, or execute arbitrary code via crafted GEM packages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0469
- https://exchange.xforce.ibmcloud.com/vulnerabilities/31688
- https://github.com/rubygems/rubygems
- https://web.archive.org/web/20070210090150/http://rubyforge.org/frs/shownotes.php?group_id=126&release_id=9074
- https://web.archive.org/web/20201207172116/http://www.securityfocus.com/archive/1/458128/100/0/threaded
- http://marc.info/?l=full-disclosure&m=116939816621060&w=2
- http://www.novell.com/linux/security/advisories/2007_4_sr.html
