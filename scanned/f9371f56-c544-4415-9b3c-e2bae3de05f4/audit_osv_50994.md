# [H] CVE-2020-6821

## Summary
Severity: High
Advisory: CVE-2020-6821
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-24
Source: https://osv.dev/vulnerability/CVE-2020-6821
Type: osv

## Details
When reading from areas partially or fully outside the source resource with WebGL's <code>copyTexSubImage</code> method, the specification requires the returned values be zero. Previously, this memory was uninitialized, leading to potentially sensitive data disclosure. This vulnerability affects Thunderbird < 68.7.0, Firefox ESR < 68.7, and Firefox < 75.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-14/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-12/
- https://www.mozilla.org/security/advisories/mfsa2020-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1625404
