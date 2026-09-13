# [H] CVE-2022-0517

## Summary
Severity: High
Advisory: CVE-2022-0517
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-0517
Type: osv

## Details
Mozilla VPN can load an OpenSSL configuration file from an unsecured directory. A user or attacker with limited privileges could leverage this to launch arbitrary code with SYSTEM privilege. This vulnerability affects Mozilla VPN < 2.7.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0517.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0517
- https://www.mozilla.org/security/advisories/mfsa2022-08/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1752291
