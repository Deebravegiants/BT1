# [H] CVE-2023-23846

## Summary
Severity: High
Advisory: CVE-2023-23846
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-01
Source: https://osv.dev/vulnerability/CVE-2023-23846
Type: osv

## Details
Due to insufficient length validation in the Open5GS GTP library versions prior to versions 2.4.13 and 2.5.7, when parsing extension headers in GPRS tunneling protocol (GPTv1-U) messages, a protocol payload with any extension header length set to zero causes an infinite loop. The affected process becomes immediately unresponsive, resulting in denial of service and excessive resource consumption. CVSS3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/E:P/RL:O/RC:C

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23846.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23846
- https://www.synopsys.com/blogs/software-security/cyrc-advisory-open5gs-gtp-library/
