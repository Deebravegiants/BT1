# [C] CVE-2019-3563

## Summary
Severity: Critical
Advisory: CVE-2019-3563
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/CVE-2019-3563
Type: osv

## Details
Wangle's LineBasedFrameDecoder contains logic for identifying newlines which incorrectly advances a buffer, leading to a potential underflow. This affects versions of Wangle prior to v2019.04.22.00

## References
- https://github.com/facebook/wangle/commit/5b3bceca875e4ea4ed9d14c20b20ce46c92c13c6
