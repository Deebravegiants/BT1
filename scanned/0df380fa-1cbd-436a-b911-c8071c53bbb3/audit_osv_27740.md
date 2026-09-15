# [H] CVE-2024-25389

## Summary
Severity: High
Advisory: CVE-2024-25389
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-25389
Type: osv

## Details
RT-Thread through 5.0.2 generates random numbers with a weak algorithm of "seed = 214013L * seed + 2531011L; return (seed >> 16) & 0x7FFF;" in calc_random in drivers/misc/rt_random.c.

## References
- http://seclists.org/fulldisclosure/2024/Mar/28
- https://github.com/hnsecurity/vulns/blob/main/HNS-2024-05-rt-thread.txt
- https://seclists.org/fulldisclosure/2024/Mar/28
- https://security.humanativaspa.it/multiple-vulnerabilities-in-rt-thread-rtos/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25389.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25389
- https://github.com/RT-Thread/rt-thread/issues/8283
- http://www.openwall.com/lists/oss-security/2024/03/05/1
