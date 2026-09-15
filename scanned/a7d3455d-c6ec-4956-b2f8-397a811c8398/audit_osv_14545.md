# [C] CVE-2019-1010228

## Summary
Severity: Critical
Advisory: CVE-2019-1010228
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-22
Source: https://osv.dev/vulnerability/CVE-2019-1010228
Type: osv

## Details
OFFIS.de DCMTK 3.6.3 and below is affected by: Buffer Overflow. The impact is: Possible code execution and confirmed Denial of Service. The component is: DcmRLEDecoder::decompress() (file dcrledec.h, line 122). The attack vector is: Many scenarios of DICOM file processing (e.g. DICOM to image conversion). The fixed version is: 3.6.4, after commit 40917614e.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NQOAULR72EYJQ4HS6YGLK2S6YNEXY2ET/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PBKP2O24CTYIANEJTP4TVEPYEVSYV2RX/
- https://support.dcmtk.org/redmine/issues/858
