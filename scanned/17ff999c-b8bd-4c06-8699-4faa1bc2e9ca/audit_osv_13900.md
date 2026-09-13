# [M] CVE-2018-3988

## Summary
Severity: Medium
Advisory: CVE-2018-3988
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-3988
Type: osv

## Details
Signal Messenger for Android 4.24.8 may expose private information when using "disappearing messages." If a user uses the photo feature available in the "attach file" menu, then Signal will leave the picture in its own cache directory, which is available to any application on the system.

## References
- http://www.securityfocus.com/bid/106207
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0656
