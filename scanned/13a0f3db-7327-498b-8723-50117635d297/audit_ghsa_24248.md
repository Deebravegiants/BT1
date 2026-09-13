# [H] Phusion Passenger Race Condition Allows Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-jjcj-fgfm-9g9r
CVE: CVE-2018-12029
CWE: CWE-362
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jjcj-fgfm-9g9r
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=3.0.0 <5.3.2

## Details
A race condition in the nginx module in Phusion Passenger 3.x through 5.x before 5.3.2 allows local escalation of privileges when a non-standard passenger_instance_registry_dir with insufficiently strict permissions is configured. Replacing a file with a symlink after the file was created, but before it was chowned, leads to the target of the link being chowned via the path. Targeting sensitive files such as root's crontab file allows privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12029
- https://blog.phusion.nl/2018/06/12/passenger-5-3-2-various-security-fixes
- https://blog.phusion.nl/passenger-5-3-2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2018-12029.yml
- https://lists.debian.org/debian-lts-announce/2018/06/msg00007.html
- https://pulsesecurity.co.nz/advisories/phusion-passenger-priv-esc
- https://security.gentoo.org/glsa/201807-02
