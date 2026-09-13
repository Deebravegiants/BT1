# [H] iccDEV has Undefined Behavior in icSigCalcOp()

## Summary
Severity: High
Advisory: CVE-2026-24407
Aliases: GHSA-m6gx-93cp-4855
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-01-24
Source: https://osv.dev/vulnerability/CVE-2026-24407
Type: osv

## Details
iccDEV provides libraries and tools for interacting with, manipulating, and applying ICC color management profiles. Versions 2.3.1.1 and below have Undefined Behavior in icSigCalcOp(). This occurs when user-controllable input is unsafely incorporated into ICC profile data or other structured binary blobs. Successful exploitation may allow an attacker to perform DoS, manipulate data, bypass application logic and Code Execution. This issue has been fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24407.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-m6gx-93cp-4855
- https://nvd.nist.gov/vuln/detail/CVE-2026-24407
- https://github.com/InternationalColorConsortium/iccDEV/issues/481
- https://github.com/InternationalColorConsortium/iccDEV/commit/881802931a71c4b0dfc28bc80ee55b2cb84dab90
