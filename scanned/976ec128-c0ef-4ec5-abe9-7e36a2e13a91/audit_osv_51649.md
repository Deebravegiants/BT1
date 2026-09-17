# [M] CVE-2021-3764

## Summary
Severity: Medium
Advisory: CVE-2021-3764
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3764
Type: osv

## Details
A memory leak flaw was found in the Linux kernel's ccp_run_aes_gcm_cmd() function that allows an attacker to cause a denial of service. The vulnerability is similar to the older CVE-2019-18808. The highest threat from this vulnerability is to system availability.

## References
- https://security-tracker.debian.org/tracker/CVE-2021-3764
- https://access.redhat.com/security/cve/CVE-2021-3764
- https://bugzilla.redhat.com/show_bug.cgi?id=1997467
- https://github.com/torvalds/linux/commit/505d9dcb0f7ddf9d075e729523a33d38642ae680
