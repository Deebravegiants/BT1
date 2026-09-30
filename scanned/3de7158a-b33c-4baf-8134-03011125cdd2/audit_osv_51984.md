# [M] CVE-2021-46926

## Summary
Severity: Medium
Advisory: CVE-2021-46926
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46926
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda: intel-sdw-acpi: harden detection of controller

The existing code currently sets a pointer to an ACPI handle before
checking that it's actually a SoundWire controller. This can lead to
issues where the graph walk continues and eventually fails, but the
pointer was set already.

This patch changes the logic so that the information provided to
the caller is set when a controller is found.

## References
- https://git.kernel.org/stable/c/cce476954401e3421afafb25bbaa926050688b1d
- https://git.kernel.org/stable/c/385f287f9853da402d94278e59f594501c1d1dad
