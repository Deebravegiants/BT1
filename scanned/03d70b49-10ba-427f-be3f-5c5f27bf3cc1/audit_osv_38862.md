# [M] Possible Out of Bounds Read in X509_VERIFY_PARAM_set1_email()

## Summary
Severity: Medium
Advisory: CVE-2026-42771
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-42771
Type: osv

## Details
Issue summary: When the X509_VERIFY_PARAM_set1_email is called by an
application to validate a crafted e-mail address, such as during S/MIME
message validation, an out of bounds read can happen.

Impact summary: This out of bounds read will not directly exfiltrate
the data read to the attacker so the most likely result is a crash and
a Denial of Service.

An internal helper function called from X509_VERIFY_PARAM_[set|add]_email()
used a wrong length when validating the local part of an email address.
This could cause the 64 octet limit on the local part of an email address
to be not enforced, or cause an out of bound read and potentially a crash.

The bug is reachable via S-MIME validation with a crafted From: address
supplied in an email message that can potentially cause a crash.

No FIPS modules are affected by this issue as the affected code is outside
the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42771.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42771
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/6cd187689f8180c1f8a3acde21f88190c4a20de7
