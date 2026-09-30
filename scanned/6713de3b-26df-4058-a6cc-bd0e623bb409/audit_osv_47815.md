# [M] CVE-2017-12951

## Summary
Severity: Medium
Advisory: CVE-2017-12951
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2017-12951
Type: osv

## Details
The gig::DimensionRegion::CreateVelocityTable function in gig.cpp in libgig 4.0.0 allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) via a crafted gig file.

## References
- https://www.exploit-db.com/exploits/42546/
- http://seclists.org/fulldisclosure/2017/Aug/39
