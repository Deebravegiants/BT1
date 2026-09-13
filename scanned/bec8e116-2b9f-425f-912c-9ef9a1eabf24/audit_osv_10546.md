# [H] CVE-2017-16933

## Summary
Severity: High
Advisory: CVE-2017-16933
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-24
Source: https://osv.dev/vulnerability/CVE-2017-16933
Type: osv

## Details
etc/initsystem/prepare-dirs in Icinga 2.x through 2.8.1 has a chown call for a filename in a user-writable directory, which allows local users to gain privileges by leveraging access to the $ICINGA2_USER account for creation of a link.

## References
- https://github.com/Icinga/icinga2/issues/5793
