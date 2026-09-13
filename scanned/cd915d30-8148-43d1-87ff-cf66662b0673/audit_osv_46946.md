# [C] CVE-2015-8396

## Summary
Severity: Critical
Advisory: CVE-2015-8396
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-01-12
Source: https://osv.dev/vulnerability/CVE-2015-8396
Type: osv

## Details
Integer overflow in the ImageRegionReader::ReadIntoBuffer function in MediaStorageAndFileFormat/gdcmImageRegionReader.cxx in Grassroots DICOM (aka GDCM) before 2.6.2 allows attackers to execute arbitrary code via crafted header dimensions in a DICOM image file, which triggers a buffer overflow.

## References
- http://census-labs.com/news/2016/01/11/gdcm-buffer-overflow-imageregionreaderreadintobuffer/
- http://sourceforge.net/p/gdcm/mailman/message/34670701/
- http://sourceforge.net/p/gdcm/mailman/message/34687533/
- http://packetstormsecurity.com/files/135205/GDCM-2.6.0-2.6.1-Integer-Overflow.html
- http://seclists.org/fulldisclosure/2016/Jan/29
- http://sourceforge.net/p/gdcm/gdcm/ci/e547b1ded3fd21e0b0ad149f13045aa12d4b9b7c/
- http://www.securityfocus.com/archive/1/537264/100/0/threaded
- https://www.exploit-db.com/exploits/39229/
