# [M] CVE-2010-2449

## Summary
Severity: Medium
Advisory: CVE-2010-2449
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2010-2449
Type: osv

## Details
Gource through 0.26 logs to a predictable file name (/tmp/gource-$UID.tmp), enabling attackers to overwrite an arbitrary file via a symlink attack.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=577958
- https://security-tracker.debian.org/tracker/CVE-2010-2449
- https://www.securityfocus.com/bid/39529/info
