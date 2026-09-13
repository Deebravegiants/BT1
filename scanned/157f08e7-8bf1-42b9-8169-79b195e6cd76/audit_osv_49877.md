# [M] CVE-2019-20633

## Summary
Severity: Medium
Advisory: CVE-2019-20633
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2019-20633
Type: osv

## Details
GNU patch through 2.7.6 contains a free(p_line[p_end]) Double Free vulnerability in the function another_hunk in pch.c that can cause a denial of service via a crafted patch file. NOTE: this issue exists because of an incomplete fix for CVE-2018-6952.

## References
- https://savannah.gnu.org/bugs/index.php?56683
