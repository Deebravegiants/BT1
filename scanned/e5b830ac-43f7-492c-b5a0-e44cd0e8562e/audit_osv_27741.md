# [M] CVE-2024-25394

## Summary
Severity: Medium
Advisory: CVE-2024-25394
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-25394
Type: osv

## Details
A buffer overflow occurs in utilities/ymodem/ry_sy.c in RT-Thread through 5.0.2 because of an incorrect sprintf call or a missing '\0' character.

## References
- http://seclists.org/fulldisclosure/2024/Mar/28
- https://github.com/hnsecurity/vulns/blob/main/HNS-2024-05-rt-thread.txt
- https://seclists.org/fulldisclosure/2024/Mar/28
- https://security.humanativaspa.it/multiple-vulnerabilities-in-rt-thread-rtos/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25394.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25394
- https://github.com/RT-Thread/rt-thread/issues/8291
- http://www.openwall.com/lists/oss-security/2024/03/05/1
