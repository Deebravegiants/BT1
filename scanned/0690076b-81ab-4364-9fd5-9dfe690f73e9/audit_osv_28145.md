# [C] Manipulated DATA Submessage causes a heap-buffer-overflow error

## Summary
Severity: Critical
Advisory: CVE-2024-28231
Aliases: GHSA-9m2j-qw67-ph4w
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-28231
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the Data Distribution Service standard of the Object Management Group. Prior to versions 2.14.0, 2.13.4, 2.12.3, 2.10.4, and 2.6.8, manipulated DATA Submessage can cause a heap overflow error in the Fast-DDS process, causing the process to be terminated remotely. Additionally, the payload_size in the DATA Submessage packet is declared as uint32_t. When a negative number, such as -1, is input into this variable, it results in an Integer Overflow (for example, -1 gets converted to 0xFFFFFFFF). This eventually leads to a heap-buffer-overflow, causing the program to terminate. Versions 2.14.0, 2.13.4, 2.12.3, 2.10.4, and 2.6.8 contain a fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28231.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-9m2j-qw67-ph4w
- https://nvd.nist.gov/vuln/detail/CVE-2024-28231
- https://github.com/eProsima/Fast-DDS/commit/355706386f4af9ce74125eeec3c449b06113112b
