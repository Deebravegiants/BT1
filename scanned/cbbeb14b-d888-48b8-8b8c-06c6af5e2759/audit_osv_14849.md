# [H] CVE-2019-11922

## Summary
Severity: High
Advisory: CVE-2019-11922
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-11922
Type: osv

## Details
A race condition in the one-pass compression functions of Zstandard prior to version 1.3.8 could allow an attacker to write bytes out of bounds if an output buffer smaller than the recommended size was used.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00078.html
- https://usn.ubuntu.com/4108-1/
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.facebook.com/security/advisories/cve-2019-11922
- https://github.com/facebook/zstd/pull/1404/commits/3e5cdf1b6a85843e991d7d10f6a2567c15580da0
