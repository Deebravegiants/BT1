# [M] TorBot vulnerable to Inefficient Regular Expression Complexity in validate_link

## Summary
Severity: Medium
Advisory: GHSA-72qw-p7hh-m3ff
CVE: CVE-2023-45813
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-72qw-p7hh-m3ff
Type: github-advisory

## Affected
- PyPI: `torbot` — affected >=0 <4.0.0

## Details
### Summary
_The torbot.modules.validators.validate_link function uses the python-validators URL validation regex. This particular regular expression has an exponential complexity which allows an attacker to cause an application crash using a well-crafted argument.._

### Details
https://github.com/DedSecInside/TorBot/blob/d2b89192379ad033ffc7044efff26e16ccc02d5a/torbot/modules/validators.py#L13

An attacker can use a well-crafted URL argument to exploit the vulnerability in the regular expression and cause a Denial of Service on the system.

### PoC
I have uploaded a secret gist containing a PoC (https://gist.github.com/ikkebr/6041055314f1cfb8e65b2a1acbaae12c). By adding one special character at the end of the user argument of the URL, the regular expression will take exponentially longer to compute.

For a string of size 10k, the regex will take 0.01s without the well-crafted URL and 1.3s with the well-crafted URL exploit.
For a string of size 50k, the regex will take 0.03s without the well-crafted URL and 35s with the well-crafted URL exploit.
For a string of size 100k, the regex will take 0.05s without the well-crafted URL and over 200s with the well-crafted URL exploit.

The regular expression used in the validators library versions [0.20, 0.11] is vulnerable to this attack. Version 0.21 appears to be unaffected, but it no longer contains a single regular expression.

### Impact
An attacker could exploit this vulnerability to cause a denial of service or increased resource usage.

## References
- https://github.com/DedSecInside/TorBot/security/advisories/GHSA-72qw-p7hh-m3ff
- https://nvd.nist.gov/vuln/detail/CVE-2023-45813
- https://github.com/DedSecInside/TorBot/commit/ef6e06bc7785355b1701d5524eb4550441086ac4
- https://gist.github.com/ikkebr/6041055314f1cfb8e65b2a1acbaae12c
- https://github.com/DedSecInside/TorBot
- https://github.com/DedSecInside/TorBot/blob/d2b89192379ad033ffc7044efff26e16ccc02d5a/torbot/modules/validators.py#L13
