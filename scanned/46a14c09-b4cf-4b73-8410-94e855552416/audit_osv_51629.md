# [C] CVE-2021-3643

## Summary
Severity: Critical
Advisory: CVE-2021-3643
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/CVE-2021-3643
Type: osv

## Details
A flaw was found in sox 14.4.1. The lsx_adpcm_init function within libsox leads to a global-buffer-overflow. This flaw allows an attacker to input a malicious file, leading to the disclosure of sensitive information.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1980626
