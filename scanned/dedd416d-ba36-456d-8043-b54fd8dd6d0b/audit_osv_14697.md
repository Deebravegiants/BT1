# [C] CVE-2019-10878

## Summary
Severity: Critical
Advisory: CVE-2019-10878
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-05
Source: https://osv.dev/vulnerability/CVE-2019-10878
Type: osv

## Details
In Teeworlds 0.7.2, there is a failed bounds check in CDataFileReader::GetData() and CDataFileReader::ReplaceData() and related functions in engine/shared/datafile.cpp that can lead to an arbitrary free and out-of-bounds pointer write, possibly resulting in remote code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00077.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5KCS2CFDYJFBLZ4QKVPNJWHOZEGQ2LBC/
- https://github.com/teeworlds/teeworlds/issues/2073
