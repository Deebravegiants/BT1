# [M] CVE-2023-46046

## Summary
Severity: Medium
Advisory: CVE-2023-46046
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-46046
Type: osv

## Details
An issue in MiniZinc before 2.8.0 allows a NULL pointer dereference via ti_expr in a crafted .mzn file. NOTE: this is disputed because there is no common libminizinc use case in which an unattended process is supposed to run forever to process a series of atttacker-controlled .mzn files.

## References
- http://packetstormsecurity.com/files/176817/MiniZinc-2.7.6-Null-Pointer.html
- https://www.minizinc.org/doc-2.8.3/en/changelog.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46046.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-46046
- https://github.com/MiniZinc/libminizinc/issues/730
- https://github.com/MiniZinc/libminizinc/commit/afe67acc20898e4308044b54c4acf7a08df544f0
- http://seclists.org/fulldisclosure/2024/Jan/63
