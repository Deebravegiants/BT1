# [C] CVE-2021-40373

## Summary
Severity: Critical
Advisory: CVE-2021-40373
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-10
Source: https://osv.dev/vulnerability/CVE-2021-40373
Type: osv

## Details
playSMS before 1.4.5 allows Arbitrary Code Execution by entering PHP code at the #tabs-information-page of core_main_config, and then executing that code via the index.php?app=main&inc=core_welcome URI.

## References
- https://playsms.org/2021/09/04/playsms-1-4-5-released/
- https://github.com/maikroservice/CVE-2021-40373
