# [H] CVE-2023-49552

## Summary
Severity: High
Advisory: CVE-2023-49552
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-49552
Type: osv

## Details
An Out of Bounds Write in Cesanta mjs 2.20.0 allows a remote attacker to cause a denial of service via the mjs_op_json_stringify function in the msj.c file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49552.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49552
- https://github.com/cesanta/mjs/issues/256
