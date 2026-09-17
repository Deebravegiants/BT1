# [M] gmrtd ReadFile Vulnerable to Denial of Service via Excessive TLV Length Values

## Summary
Severity: Medium
Advisory: GHSA-j49h-6577-5xwq
CVE: CVE-2026-24738
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-j49h-6577-5xwq
Type: github-advisory

## Affected
- Go: `github.com/gmrtd/gmrtd` — affected >=0 <0.17.2

## Details
# Unbounded TLV length in ReadFile can cause Denial of Service

## Summary

A Denial of Service vulnerability was identified in `ReadFile()` where unbounded TLV length values could lead to excessive CPU and memory usage when processing data from a malicious or non-compliant NFC source. This issue has been fixed by enforcing strict limits on acceptable TLV lengths.

## Affected Versions

- **Affected:** All versions prior to **v0.17.2**
- **Fixed in:** **v0.17.2**

## Details

`ReadFile()` processes BER-TLV encoded data returned from an NFC or APDU source via a `Transceiver` interface. Prior to the fix, the implementation did not enforce an upper bound on long-form TLV length values.

A malicious or non-compliant NFC endpoint could advertise an excessively large length (up to 4 GB), causing the library to:

- Perform a very large number of read iterations  
- Allocate excessive memory  
- Consume significant CPU resources  
- Block execution for an extended period  

While such lengths are unrealistic for compliant MRTD or ISO 7816 devices, they can be produced by emulated or malicious sources, or by untrusted inputs routed through higher-level APIs.

## Impact

Applications using `gmrtd` to read data from NFC or APDU sources may experience:

- Excessive CPU usage  
- Memory exhaustion  
- Application hangs or denial of service  

No confidentiality or data integrity impact has been identified.

## Resolution

This issue has been resolved in **v0.17.2**.

The fix introduces:

- Enforcement of maximum allowable TLV lengths  
- Upper bounds on the number of read operations required to retrieve a file  
- Rejection of APDUs that exceed the requested response length  

## Recommendation

Users should **upgrade to v0.17.2 or later**.

No additional mitigation is required once the library is updated.

## Credits

Discovered and reported by **@ramrunner**.

## References
- https://github.com/gmrtd/gmrtd/security/advisories/GHSA-j49h-6577-5xwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-24738
- https://github.com/gmrtd/gmrtd/commit/54469a95e5a20a8602ac1457b2110bfeb80c8891
- https://github.com/gmrtd/gmrtd
- https://github.com/gmrtd/gmrtd/releases/tag/v0.17.2
