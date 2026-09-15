# [H] String::Compare::ConstantTime for Perl through 0.321 is vulnerable to timing attacks that allow an attacker to guess the length of a secret string

## Summary
Severity: High
Advisory: CVE-2024-13939
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2024-13939
Type: osv

## Details
String::Compare::ConstantTime for Perl through 0.321 is vulnerable to timing attacks that allow an attacker to guess the length of a secret string.

As stated in the documentation: "If the lengths of the strings are different, because equals returns false right away the size of the secret string may be leaked (but not its contents)."

This is similar to CVE-2020-36829

## References
- https://cpan.org/modules
- https://metacpan.org/release/FRACTAL/String-Compare-ConstantTime-0.321/view/lib/String/Compare/ConstantTime.pm#TIMING-SIDE-CHANNEL
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/13xxx/CVE-2024-13939.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-13939
- https://github.com/hoytech/String-Compare-ConstantTime
