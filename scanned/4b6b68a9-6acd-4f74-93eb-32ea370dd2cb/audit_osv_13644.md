# [M] CVE-2018-20681

## Summary
Severity: Medium
Advisory: CVE-2018-20681
CVSS: 6.1 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/CVE-2018-20681
Type: osv

## Details
mate-screensaver before 1.20.2 in MATE Desktop Environment allows physically proximate attackers to view screen content and possibly control applications. By unplugging and re-plugging or power-cycling external output devices (such as additionally attached graphical outputs via HDMI, VGA, DVI, etc.) the content of a screensaver-locked session can be revealed. In some scenarios, the attacker can execute applications, such as by clicking with a mouse.

## References
- https://github.com/mate-desktop/mate-screensaver/issues/170
- https://github.com/mate-desktop/mate-screensaver/issues/152
- https://github.com/mate-desktop/mate-screensaver/pull/167
- https://github.com/mate-desktop/mate-screensaver/issues/155
