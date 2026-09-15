# [M] CVE-2018-15800

## Summary
Severity: Medium
Advisory: CVE-2018-15800
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-15800
Type: osv

## Details
Cloud Foundry Bits Service, versions prior to 2.18.0, includes an information disclosure vulnerability. A remote malicious user may execute a timing attack to brute-force the signing key, allowing them complete read and write access to the the Bits Service storage.

## References
- https://www.cloudfoundry.org/blog/cve-2018-15800
