# [M] CVE-2016-3695

## Summary
Severity: Medium
Advisory: CVE-2016-3695
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-29
Source: https://osv.dev/vulnerability/CVE-2016-3695
Type: osv

## Details
The einj_error_inject function in drivers/acpi/apei/einj.c in the Linux kernel allows local users to simulate hardware errors and consequently cause a denial of service by leveraging failure to disable APEI error injection through EINJ when securelevel is set.

## References
- http://www.securityfocus.com/bid/102327
- https://bugzilla.redhat.com/show_bug.cgi?id=1322755
- https://github.com/mjg59/linux/commit/d7a6be58edc01b1c66ecd8fcc91236bfbce0a420
