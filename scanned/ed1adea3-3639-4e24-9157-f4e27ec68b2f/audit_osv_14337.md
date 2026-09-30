# [H] CVE-2018-9154

## Summary
Severity: High
Advisory: CVE-2018-9154
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-04
Source: https://osv.dev/vulnerability/CVE-2018-9154
Type: osv

## Details
There is a reachable abort in the function jpc_dec_process_sot in libjasper/jpc/jpc_dec.c of JasPer 2.0.14 that will lead to a remote denial of service attack by triggering an unexpected jas_alloc2 return value, a different vulnerability than CVE-2017-13745.

## References
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://security.gentoo.org/glsa/201908-03
- https://drive.google.com/drive/u/2/folders/1YuxdfbZrw79kfzoQz0PpxIutZ7pkf_kW
