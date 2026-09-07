# [M] Argument injection in lettre

## Summary
Severity: Medium
Advisory: GHSA-vc2p-r46x-m3vx
CVE: CVE-2020-28247
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vc2p-r46x-m3vx
Type: github-advisory

## Affected
- crates.io: `lettre` — affected >=0.9.0 <0.9.5
- crates.io: `lettre` — affected >=0.8.0 <0.8.4
- crates.io: `lettre` — affected >=0.7.0 <0.7.1

## Details
### Impact

Affected versions of lettre allowed argument injection to the sendmail command. It was possible, using forged to addresses, to pass arbitrary arguments to the sendmail executable.

Depending on the implementation (original sendmail, postfix, exim, etc.) it could be possible in some cases to write email data into abritrary files (using sendmail's logging features).

*NOTE*: This vulnerability only affects the sendmail transport. Others, including smtp, are not affected.

### Fix

The flaw is corrected by modifying the executed command to stop parsing arguments before passing the destination addresses.

### References

* [RUSTSEC-2020-0069](https://rustsec.org/advisories/RUSTSEC-2020-0069.html)
* [CVE-2020-28247](https://nvd.nist.gov/vuln/detail/CVE-2020-28247)

## References
- https://github.com/lettre/lettre/security/advisories/GHSA-vc2p-r46x-m3vx
- https://nvd.nist.gov/vuln/detail/CVE-2020-28247
- https://github.com/RustSec/advisory-db/pull/478/files
- https://github.com/lettre/lettre/pull/508/commits/bbe7cc5381c5380b54fb8bbb4f77a3725917ff0b
- https://github.com/lettre/lettre
- https://rustsec.org/advisories/RUSTSEC-2020-0069.html
