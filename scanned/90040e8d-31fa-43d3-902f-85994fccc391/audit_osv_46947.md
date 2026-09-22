# [H] CVE-2015-8397

## Summary
Severity: High
Advisory: CVE-2015-8397
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-01-12
Source: https://osv.dev/vulnerability/CVE-2015-8397
Type: osv

## Details
The JPEGLSCodec::DecodeExtent function in MediaStorageAndFileFormat/gdcmJPEGLSCodec.cxx in Grassroots DICOM (aka GDCM) before 2.6.2 allows remote attackers to obtain sensitive information from process memory or cause a denial of service (application crash) via an embedded JPEG-LS image with dimensions larger than the selected region in a (1) two-dimensional or (2) three-dimensional DICOM image file, which triggers an out-of-bounds read.

## References
- http://census-labs.com/news/2016/01/11/gdcm-out-bounds-read-jpeglscodec-decodeextent/
- http://packetstormsecurity.com/files/135206/GDCM-2.6.0-2.6.1-Out-Of-Bounds-Read.html
- http://seclists.org/fulldisclosure/2016/Jan/33
- http://sourceforge.net/p/gdcm/gdcm/ci/e547b1ded3fd21e0b0ad149f13045aa12d4b9b7c/
- http://sourceforge.net/p/gdcm/mailman/message/34670701/
- http://sourceforge.net/p/gdcm/mailman/message/34687533/
- http://www.securityfocus.com/archive/1/537263/100/0/threaded
- http://seclists.org/fulldisclosure/2016/Jan/33
- http://census-labs.com/news/2016/01/11/gdcm-out-bounds-read-jpeglscodec-decodeextent/
- http://sourceforge.net/p/gdcm/mailman/message/34670701/
- http://sourceforge.net/p/gdcm/mailman/message/34687533/
- http://sourceforge.net/p/gdcm/gdcm/ci/e547b1ded3fd21e0b0ad149f13045aa12d4b9b7c/
