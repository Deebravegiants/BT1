# [M] Catastrophic backtracking in regex allows Denial of Service in Waitress

## Summary
Severity: Medium
Advisory: GHSA-73m2-3pwg-5fgc
CVE: CVE-2020-5236
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-02-04
Source: https://github.com/advisories/GHSA-73m2-3pwg-5fgc
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=1.4.2 <1.4.3

## Details
### Impact

When waitress receives a header that contains invalid characters it will cause the regular expression engine to catastrophically backtrack causing the process to use 100% CPU time and blocking any other interactions.

This would allow an attacker to send a single request with an invalid header and take the service offline.

Invalid header example:

```
Bad-header: xxxxxxxxxxxxxxx\x10
```

Increasing the number of `x`'s in the header will increase the amount of time Waitress spends in the regular expression engine.

This issue was introduced in version 1.4.2 when the regular expression was updated to attempt to match the behaviour required by errata associated with RFC7230.

### Patches

The regular expression that is used to validate incoming headers has been updated in version 1.4.3, it is recommended that people upgrade to the new version of Waitress as soon as possible.

### Workarounds

If you have deployed a reverse proxy in front of Waitress it may already be rejecting requests that include invalid headers.

### Thanks

The Pylons Project would like to thank [Fil Zembowicz](https://github.com/fzembow) for reaching out and disclosing this vulnerability!

### References

Catastrophic backtracking explained: https://www.regular-expressions.info/catastrophic.html

### For more information
If you have any questions or comments about this advisory:

- open an issue at https://github.com/Pylons/waitress/issues (if not sensitive or security related)
- email the Pylons Security mailing list: pylons-project-security@googlegroups.com (if security related)

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-73m2-3pwg-5fgc
- https://nvd.nist.gov/vuln/detail/CVE-2020-5236
- https://github.com/Pylons/waitress/commit/6e46f9e3f014d64dd7d1e258eaf626e39870ee1f
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2020-155.yaml
