# [H] CVE-2022-49737

## Summary
Severity: High
Advisory: CVE-2022-49737
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2025-03-16
Source: https://osv.dev/vulnerability/CVE-2022-49737
Type: osv

## Details
In X.Org X server 20.11 through 21.1.16, when a client application uses easystroke for mouse gestures, the main thread modifies various data structures used by the input thread without acquiring a lock, aka a race condition. In particular, AttachDevice in dix/devices.c does not acquire an input lock.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?att=1;bug=1081338;filename=dix-Hold-input-lock-for-AttachDevice.patch;msg=5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1081338
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49737.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49737
- https://gitlab.freedesktop.org/xorg/xserver/-/issues/1260
- https://gitlab.freedesktop.org/xorg/xserver/-/commit/dc7cb45482cea6ccec22d117ca0b489500b4d0a0
