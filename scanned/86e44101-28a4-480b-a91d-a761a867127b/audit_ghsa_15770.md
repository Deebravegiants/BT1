# [H] audify vulnerable to Improper Validation of Array Index

## Summary
Severity: High
Advisory: GHSA-7vhm-fmph-7wxw
CVE: CVE-2024-21522
CWE: CWE-129
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-7vhm-fmph-7wxw
Type: github-advisory

## Affected
- npm: `audify` — affected >=0

## Details
All versions of the package audify are vulnerable to Improper Validation of Array Index when frameSize is provided to the new OpusDecoder().decode or new OpusDecoder().decodeFloat functions it is not checked for negative values. This can lead to a process crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21522
- https://gist.github.com/dellalibera/6bb866ae5d1cc2adaabe27bbd6d2d21e
- https://github.com/almoghamdani/audify
- https://github.com/almoghamdani/audify/blob/94b2fe79dc528fda2c7d59c7a0fd0e9de07dc3dc/src/opus_decoder.cpp#L53
- https://github.com/almoghamdani/audify/blob/94b2fe79dc528fda2c7d59c7a0fd0e9de07dc3dc/src/opus_decoder.cpp%23L79
- https://security.snyk.io/vuln/SNYK-JS-AUDIFY-6370700
