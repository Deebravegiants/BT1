# [C] CVE-2022-44542

## Summary
Severity: Critical
Advisory: CVE-2022-44542
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-44542
Type: osv

## Details
lesspipe before 2.06 allows attackers to execute code via Perl Storable (pst) files, because of deserialized object destructor execution via a key/value pair in a hash.

## References
- https://bugs.gentoo.org/865631
- https://github.com/wofr06/lesspipe/releases/tag/v2.06
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44542.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44542
- https://security.gentoo.org/glsa/202211-02
