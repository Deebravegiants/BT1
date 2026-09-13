# [H] CVE-2018-14345

## Summary
Severity: High
Advisory: CVE-2018-14345
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14345
Type: osv

## Details
An issue was discovered in SDDM through 0.17.0. If configured with ReuseSession=true, the password is not checked for users with an already existing session. Any user with access to the system D-Bus can therefore unlock any graphical session. This is related to daemon/Display.cpp and helper/backend/PamBackend.cpp.

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1101450
- https://github.com/sddm/sddm/commit/147cec383892d143b5e02daa70f1e7def50f5d98
