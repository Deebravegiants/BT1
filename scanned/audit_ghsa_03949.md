# [H] Downloads Resources over HTTP in webrtc-native

## Summary
Severity: High
Advisory: GHSA-7xvg-m3vx-2hhv
CVE: CVE-2016-10600
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-7xvg-m3vx-2hhv
Type: github-advisory

## Affected
- npm: `webrtc-native` — affected >=0

## Details
Affected versions of `webrtc-native` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `webrtc-native`.


## Recommendation

No direct patch is currently available for this vulnerability. 

However, if the native components of `webrtc-native` are built from source, this avoids download the precompiled binary, therefore mitigating the insecure download. 

The package author has provided instructions for building from source [here](https://github.com/vmolsa/webrtc-native/wiki/Getting-started#building-from-source).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10600
- https://github.com/advisories/GHSA-7xvg-m3vx-2hhv
- https://www.npmjs.com/advisories/176
