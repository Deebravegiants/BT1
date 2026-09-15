# [C] CVE-2020-25023

## Summary
Severity: Critical
Advisory: CVE-2020-25023
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-04
Source: https://osv.dev/vulnerability/CVE-2020-25023
Type: osv

## Details
An issue was discovered in Noise-Java through 2020-08-27. AESGCMOnCtrCipherState.encryptWithAd() allows out-of-bounds access.

## References
- http://packetstormsecurity.com/files/159056/Noise-Java-AESGCMOnCtrCipherState.encryptWithAd-Insufficient-Boundary-Checks.html
- http://seclists.org/fulldisclosure/2020/Sep/13
- https://github.com/rweather/noise-java/pull/12
- https://github.com/rweather/noise-java/commit/18e86b6f8bea7326934109aa9ffa705ebf4bde90
