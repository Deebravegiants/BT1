# [H] XStream is vulnerable to a Denial of Service attack due to stack overflow from a manipulated binary input stream

## Summary
Severity: High
Advisory: GHSA-hfq9-hggm-c56q
CVE: CVE-2024-47072
CWE: CWE-121, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-hfq9-hggm-c56q
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.21

## Details
### Impact
The vulnerability may allow a remote attacker to terminate the application with a stack overflow error resulting in a denial of service only by manipulating the processed input stream when XStream is configured to use the BinaryStreamDriver.

### Patches
XStream 1.4.21 detects the manipulation in the binary input stream causing the the stack overflow and raises an InputManipulationException instead.

### Workarounds
The only solution is to catch the StackOverflowError in the client code calling XStream if XStream is configured to use the BinaryStreamDriver.

### References
See full information about the nature of the vulnerability and the steps to reproduce it in XStream's documentation for [CVE-2024-47072](https://x-stream.github.io/CVE-2024-47072.html).

### Credits
Alexis Challande of Trail Of Bits found and reported the issue to XStream and provided the required information to reproduce it.

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-hfq9-hggm-c56q
- https://nvd.nist.gov/vuln/detail/CVE-2024-47072
- https://github.com/x-stream/xstream/commit/bb838ce2269cac47433e31c77b2b236466e9f266
- https://github.com/x-stream/xstream/commit/fdd9f7d3de0d7ccf2f9979bcd09fbf3e6a0c881a
- https://github.com/x-stream/xstream
- https://lists.debian.org/debian-lts-announce/2024/12/msg00023.html
- https://x-stream.github.io/CVE-2024-47072.html
