# [M] YFCMF Ajax.php path traversal

## Summary
Severity: Medium
Advisory: CVE-2023-3057
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-3057
Type: osv

## Details
A vulnerability was found in YFCMF up to 3.0.4. It has been rated as problematic. This issue affects some unknown processing of the file app/admin/controller/Ajax.php. The manipulation of the argument controllername leads to path traversal: '../filedir'. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-230543.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3057.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3057
- https://vuldb.com/?id.230543
- https://vuldb.com/?ctiid.230543
- https://github.com/HuBenLab/HuBenVulList/blob/main/YFCMF-TP6-3.0.4%20has%20a%20Remote%20Command%20Execution%20(RCE)%20vulnerability%202.md
