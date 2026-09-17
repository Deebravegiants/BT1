# [C] SMTP command injection in lettre

## Summary
Severity: Critical
Advisory: GHSA-qc36-q22q-cjw3
CVE: CVE-2021-38189
CWE: CWE-147
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-12
Source: https://github.com/advisories/GHSA-qc36-q22q-cjw3
Type: github-advisory

## Affected
- crates.io: `lettre` — affected >=0.7.0 <0.9.6

## Details
### Impact

Affected versions of lettre allowed SMTP command injection through an attacker's controlled message body. The module for escaping lines starting with a period wouldn't catch a period that was placed after a double CRLF sequence, allowing the attacker to end the current message and write arbitrary SMTP commands after it.

### Fix

The flaw is fixed by correctly handling consecutive CRLF sequences.

### References

* [RUSTSEC-2021-0069](https://rustsec.org/advisories/RUSTSEC-2021-0069.html)

## References
- https://github.com/lettre/lettre/security/advisories/GHSA-qc36-q22q-cjw3
- https://github.com/lettre/lettre/pull/627/commits/93458d01fed0ec81c0e7b4e98e6f35961356fae2
- https://github.com/lettre/lettre/commit/8bfc20506cc5e098fe6eb3d1cafe3bea791215ce
- https://github.com/lettre/lettre
- https://rustsec.org/advisories/RUSTSEC-2021-0069.html
