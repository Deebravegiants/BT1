# [C] CVE-2020-28638

## Summary
Severity: Critical
Advisory: CVE-2020-28638
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-13
Source: https://osv.dev/vulnerability/CVE-2020-28638
Type: osv

## Details
ask_password in Tomb 2.0 through 2.7 returns a warning when pinentry-curses is used and $DISPLAY is non-empty, causing affected users' files to be encrypted with "tomb {W] Detected DISPLAY, but only pinentry-curses is found." as the encryption key.

## References
- https://github.com/dyne/Tomb/issues/385
