# [M] CVE-2021-3746

## Summary
Severity: Medium
Advisory: CVE-2021-3746
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-10-19
Source: https://osv.dev/vulnerability/CVE-2021-3746
Type: osv

## Details
A flaw was found in the libtpms code that may cause access beyond the boundary of internal buffers. The vulnerability is triggered by specially-crafted TPM2 command packets that then trigger the issue when the state of the TPM2's volatile state is written. The highest threat from this vulnerability is to system availability. This issue affects libtpms versions before 0.8.5, before 0.7.9 and before 0.6.6.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1998588
