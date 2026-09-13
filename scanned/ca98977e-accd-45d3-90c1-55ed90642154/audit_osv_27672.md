# [H] CVE-2024-24684

## Summary
Severity: High
Advisory: CVE-2024-24684
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-24684
Type: osv

## Details
Multiple stack-based buffer overflow vulnerabilities exist in the readOFF functionality of libigl v2.5.0. A specially crafted .off file can lead to stack-based buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.This vulnerability concerns the header parsing occuring while processing an `.off`  file via the `readOFF` function. 


We can see above that at [0] a stack-based buffer called `comment` is defined with an hardcoded size of `1000 bytes`.  The call to `fscanf` at [1] is unsafe and if the first line of the header of the `.off` files is longer than 1000 bytes it will overflow the `header` buffer.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1929
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1929
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24684.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24684
