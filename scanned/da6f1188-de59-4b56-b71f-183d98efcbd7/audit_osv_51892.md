# [H] CVE-2021-44540

## Summary
Severity: High
Advisory: CVE-2021-44540
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-44540
Type: osv

## Details
A vulnerability was found in Privoxy which was fixed in get_url_spec_param() by freeing memory of compiled pattern spec before bailing.

## References
- https://www.privoxy.org/3.0.33/user-manual/whatsnew.html%2C
- https://www.privoxy.org/gitweb/?p=privoxy.git%3Ba=commit%3Bh=652b4b7cb0
