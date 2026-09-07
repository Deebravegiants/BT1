# [M] Moodle Unauthenticated users can trigger custom messages to admin via paypal enrol script

## Summary
Severity: Medium
Advisory: GHSA-v9xq-vh72-chr4
CVE: CVE-2018-1081
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v9xq-vh72-chr4
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.11
- Packagist: `moodle/moodle` — affected >=3.2 <3.2.8
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.5
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.2

## Details
A flaw was found in Moodle 3.4 to 3.4.1, 3.3 to 3.3.4, 3.2 to 3.2.7, 3.1 to 3.1.10 and earlier unsupported versions. Unauthenticated users can trigger custom messages to admin via paypal enrol script. Paypal IPN callback script should only send error emails to admin after request origin was verified, otherwise admin email can be spammed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1081
- https://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-61392
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=367938
- http://www.securityfocus.com/bid/103728
