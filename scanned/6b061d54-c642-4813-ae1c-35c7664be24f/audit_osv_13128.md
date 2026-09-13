# [C] CVE-2018-17796

## Summary
Severity: Critical
Advisory: CVE-2018-17796
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-30
Source: https://osv.dev/vulnerability/CVE-2018-17796
Type: osv

## Details
An issue was discovered in MRCMS (aka mushroom) through 3.1.2. The WebParam.java file directly accepts the FIELD_T parameter in a request and uses it as a hash of SQL statements without filtering, resulting in a SQL injection vulnerability in getChannel() in the ChannelService.java file.

## References
- https://github.com/wuweiit/mushroom/issues/16
