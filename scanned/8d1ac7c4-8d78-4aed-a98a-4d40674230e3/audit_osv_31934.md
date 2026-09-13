# [M] can: ucan: fix out of bound read in strscpy() source

## Summary
Severity: Medium
Advisory: CVE-2025-22003
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22003
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: ucan: fix out of bound read in strscpy() source

Commit 7fdaf8966aae ("can: ucan: use strscpy() to instead of strncpy()")
unintentionally introduced a one byte out of bound read on strscpy()'s
source argument (which is kind of ironic knowing that strscpy() is meant
to be a more secure alternative :)).

Let's consider below buffers:

  dest[len + 1]; /* will be NUL terminated */
  src[len]; /* may not be NUL terminated */

When doing:

  strncpy(dest, src, len);
  dest[len] = '\0';

strncpy() will read up to len bytes from src.

On the other hand:

  strscpy(dest, src, len + 1);

will read up to len + 1 bytes from src, that is to say, an out of bound
read of one byte will occur on src if it is not NUL terminated. Note
that the src[len] byte is never copied, but strscpy() still needs to
read it to check whether a truncation occurred or not.

This exact pattern happened in ucan.

The root cause is that the source is not NUL terminated. Instead of
doing a copy in a local buffer, directly NUL terminate it as soon as
usb_control_msg() returns. With this, the local firmware_str[] variable
can be removed.

On top of this do a couple refactors:

  - ucan_ctl_payload->raw is only used for the firmware string, so
    rename it to ucan_ctl_payload->fw_str and change its type from u8 to
    char.

  - ucan_device_request_in() is only used to retrieve the firmware
    string, so rename it to ucan_get_fw_str() and refactor it to make it
    directly handle all the string termination logic.

## References
- https://git.kernel.org/stable/c/1d22a122ffb116c3cf78053e812b8b21f8852ee9
- https://git.kernel.org/stable/c/8cec9e314d3360fc1d8346297c41a6ee45cb45a9
- https://git.kernel.org/stable/c/a4994161a61bc8fd71d105c579d847cefee99262
- https://git.kernel.org/stable/c/cc29775a8a72d7f3b56cc026796ad99bd65804a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22003.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
