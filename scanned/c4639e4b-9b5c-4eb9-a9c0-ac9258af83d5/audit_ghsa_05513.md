# [H] SiYuan Vulnerable to Arbitrary File Read via File Copy Functionality

## Summary
Severity: High
Advisory: GHSA-94c7-g2fj-7682
CVE: CVE-2026-23851
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-94c7-g2fj-7682
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260118092521-f8f4b517077b

## Details
### Summary
The SiYuan Note application (v3.5.3) contains a logic vulnerability in the /api/file/globalCopyFiles endpoint. The function allows authenticated users to copy files from any location on the server's filesystem into the application's workspace without proper path validation
### Details
The vulnerability exists in the api/file.go source code. The function globalCopyFiles accepts a list of source paths (srcs) from the JSON request body. While the code checks if the source file exists using filelock.IsExist(src), it fails to validate whether the source path resides within the authorized workspace directory.


```
func globalCopyFiles(c *gin.Context) {
    // ...

    srcsArg := arg["srcs"].([]interface{})
    
    for _, src := range srcs {

        if !filelock.IsExist(src) { ... }
        

        if err := filelock.Copy(src, dest); err != nil { ... }
    }
}
```

### PoC
The following steps demonstrate how to exfiltrate the /etc/passwd file.

1. The attacker sends a request to copy the system file /etc/passwd to the root of the application workspace (/).

<img width="1537" height="357" alt="image" src="https://github.com/user-attachments/assets/7c8e5fe8-f609-4263-8685-eedf3cf22400" />

2. The attacker downloads the copied file using the standard file retrieval API, which now treats the system file as a legitimate workspace asset.

<img width="1549" height="588" alt="image" src="https://github.com/user-attachments/assets/37cac3dd-d9a9-4191-92ea-16f0424c73e1" />
<img width="756" height="337" alt="image" src="https://github.com/user-attachments/assets/c872d729-259b-4b2a-9314-8be6b2b9b26a" />


### Impact
This vulnerability allows an attacker to read arbitrary files from the server's filesystem, bypassing intended directory restrictions. By exfiltrating sensitive configuration files (such as docker-compose.yml containing database credentials) and system files (like /etc/passwd), an attacker can harvest secrets to pivot from application access to full infrastructure compromise. This results in a complete loss of confidentiality regarding both user data and the underlying server environment.

### Tested version:
<img width="1118" height="650" alt="image" src="https://github.com/user-attachments/assets/c98cbbcc-2a28-4a15-b84e-4a7120649c5e" />

### Solution

https://github.com/siyuan-note/siyuan/issues/16860

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-94c7-g2fj-7682
- https://nvd.nist.gov/vuln/detail/CVE-2026-23851
- https://github.com/siyuan-note/siyuan/issues/16860
- https://github.com/siyuan-note/siyuan/commit/b2274baba2e11c8cf8901b0c5c871e5b27f1f6dd
- https://github.com/siyuan-note/siyuan/commit/f8f4b517077b92c90c0d7b51ac11be1b34b273ad
- https://github.com/siyuan-note/siyuan
