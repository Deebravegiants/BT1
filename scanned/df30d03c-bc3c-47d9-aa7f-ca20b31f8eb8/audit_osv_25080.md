# [M] YFCMF index.php path traversal

## Summary
Severity: Medium
Advisory: CVE-2023-3056
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-3056
Type: osv

## Details
A vulnerability was found in YFCMF up to 3.0.4. It has been declared as problematic. This vulnerability affects unknown code of the file index.php. The manipulation leads to path traversal: '../filedir'. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. VDB-230542 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3056.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3056
- https://vuldb.com/?id.230542
- https://vuldb.com/?ctiid.230542
- https://github.com/HuBenLab/HuBenVulList/blob/main/YFCMF-TP6-3.0.4%20has%20a%20Remote%20Command%20Execution%20(RCE)%20vulnerability%201.md
