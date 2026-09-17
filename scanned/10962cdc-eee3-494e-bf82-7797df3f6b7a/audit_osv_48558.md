# [M] CVE-2017-9412

## Summary
Severity: Medium
Advisory: CVE-2017-9412
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-9412
Type: osv

## Details
The unpack_read_samples function in frontend/get_audio.c in LAME 3.99.5 allows remote attackers to cause a denial of service (invalid memory read and application crash) via a crafted wav file.

## References
- https://www.exploit-db.com/exploits/42390/
- http://seclists.org/fulldisclosure/2017/Jul/63
