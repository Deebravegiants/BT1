# [M] Denial of Service in Tink-cc

## Summary
Severity: Medium
Advisory: CVE-2024-4420
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H/S:N/AU:Y/V:D/RE:L/U:Green)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2024-4420
Type: osv

## Details
There exists a Denial of service vulnerability in Tink-cc in versions prior to 2.1.3.   *  An adversary can crash binaries using the crypto::tink::JsonKeysetReader in tink-cc by providing an input that is not an encoded JSON object, but still a valid encoded JSON element, for example a number or an array. This will crash as Tink just assumes any valid JSON input will contain an object.


  *  An adversary can crash binaries using the crypto::tink::JsonKeysetReader in tink-cc by providing an input containing many nested JSON objects. This may result in a stack overflow.


We recommend upgrading to version 2.1.3 or above

## References
- https://github.com/tink-crypto
- https://github.com/tink-crypto/tink-cc/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4420.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4420
- https://github.com/tink-crypto/tink-cc/issues/4
- https://github.com/google/tink
