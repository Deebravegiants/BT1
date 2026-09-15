# [C] CVE-2017-18201

## Summary
Severity: Critical
Advisory: CVE-2017-18201
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-26
Source: https://osv.dev/vulnerability/CVE-2017-18201
Type: osv

## Details
An issue was discovered in GNU libcdio before 2.0.0. There is a double free in get_cdtext_generic() in lib/driver/_cdio_generic.c.

## References
- http://www.securityfocus.com/bid/103190
- https://access.redhat.com/errata/RHSA-2018:3246
- https://git.savannah.gnu.org/cgit/libcdio.git/commit/?id=f6f9c48fb40b8a1e8218799724b0b61a7161eb1d
