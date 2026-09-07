# [H] Yamcs has Unauthenticated Directory Traversal

## Summary
Severity: High
Advisory: GHSA-9jg3-g3wh-w9pj
CVE: CVE-2026-55552
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-9jg3-g3wh-w9pj
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.0

## Details
### Attack type: 
Unauthenticated remote  

### Impact: 
Attackers can access any system files from the underlying host.

### Affected components: HttpRequestHandler.java, StaticFileHandler.java

An Unauthenticated Directory Traversal vulnerability exists in Yamcs <=5.8.6, allowing anyone to access any file on the underlying operating system. This allows unauthenticated attackers to download sensitive files and data.

<img width="2170" height="1289" alt="image" src="https://github.com/user-attachments/assets/8d426da1-5351-4240-a290-8d858be61312" />

## Steps to Reproduce:
1. Start Yamcs and login as a user
2. Paste the following URL in the browser and press enter:

```
http://localhost:8090//etc/passwd
```

3. The `/etc/passwd` file will be downloaded.

## Acknowledgements
This vulnerability was discovered by Abderrahim Dahmani while solving a STARPWN 2025 CTF challenge at DEFCON 33 offered by VisionSpace Technologies.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-9jg3-g3wh-w9pj
- https://github.com/yamcs/yamcs/commit/c7dfd24e469ae1086c23e0fe04401cb1ce4260d4
- https://github.com/yamcs/yamcs/commit/f4bc588880c166849e983aa8f65b9c8107d06091
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.11.13
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.12.0
