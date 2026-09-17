# [H] CVE-2022-35867

## Summary
Severity: High
Advisory: CVE-2022-35867
CVSS: 7.5 (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-08-03
Source: https://osv.dev/vulnerability/CVE-2022-35867
Type: osv

## Details
This vulnerability allows local attackers to escalate privileges on affected installations of xhyve. An attacker must first obtain the ability to execute high-privileged code on the target guest system in order to exploit this vulnerability. The specific flaw exists within the e1000 virtual device. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a stack-based buffer. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of the hypervisor. Was ZDI-CAN-15056.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35867.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-35867
- https://www.zerodayinitiative.com/advisories/ZDI-22-949/
