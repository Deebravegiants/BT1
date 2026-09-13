# [H] CVE-2022-44311

## Summary
Severity: High
Advisory: CVE-2022-44311
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-11-08
Source: https://osv.dev/vulnerability/CVE-2022-44311
Type: osv

## Details
html2xhtml v1.3 was discovered to contain an Out-Of-Bounds read in the function static void elm_close(tree_node_t *nodo) at procesador.c. This vulnerability allows attackers to access sensitive files or cause a Denial of Service (DoS) via a crafted html file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44311.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44311
- https://github.com/jfisteus/html2xhtml/issues/19
