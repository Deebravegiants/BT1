# [M] CVE-2016-10894

## Summary
Severity: Medium
Advisory: CVE-2016-10894
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-08-16
Source: https://osv.dev/vulnerability/CVE-2016-10894
Type: osv

## Details
xtrlock through 2.10 does not block multitouch events. Consequently, an attacker at a locked screen can send input to (and thus control) various programs such as Chromium via events such as pan scrolling, "pinch and zoom" gestures, or even regular mouse clicks (by depressing the touchpad once and then clicking with a different finger).

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00019.html
- https://bugs.debian.org/830726
