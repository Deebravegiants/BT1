# [M] Grav vulnerable to Path Traversal allowing server files backup

## Summary
Severity: Medium
Advisory: GHSA-j422-qmxp-hv94
CVE: CVE-2025-66302
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-j422-qmxp-hv94
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
### Summary
```
A path traversal vulnerability has been identified in Grav CMS, versions 1.7.49.5 , allowing authenticated attackers
 with administrative privileges to read arbitrary files on the underlying server filesystem. This vulnerability arises due
 to insufficient input sanitization in the backup tool, where user-supplied paths are not properly restricted, enabling
 access to files outside the intended webroot directory. The impact of this vulnerability depends on the privileges of 
the user account running the application.
```

### PoC
```
To accurately demonstrate the maximum potential impact of this vulnerability, the testing environment was configured in a specific way:

- Elevated Privileges: The application was run locally with the highest possible system privileges, operating under the **`root`** user account.
    
- Objective: This configuration was chosen to unequivocally show that the path traversal vulnerability is not just a theoretical issue but can lead to a complete compromise of the underlying host when combined with poor operational practices. The ability to read any file on the system is the ultimate test of the flaw's severity.
    

Proof of Concept Goal: Under these conditions, the subsequent PoC will exploit the vulnerability to read the SSH private key
 of the `root` user (`/root/.ssh/id_rsa`). The successful exfiltration of this key represents a worst-case scenario, as it would provide 
an attacker with persistent, undetectable, and complete administrative access to the host server. This highlights the critical intersection
 of an application-layer vulnerability and a infrastructure-level misconfiguration.

```




```
1- LOGIN AS ADMIN AND  GO TO  : http://127.0.0.1/admin/tools/backups
2- Change 'Root Folder' to backup directory /../../../../../../../root/.ssh/ 

```
<img width="1902" height="492" alt="Screenshot 2025-09-11 161519" src="https://github.com/user-attachments/assets/23a60dc3-7758-4e24-b910-e66a1dd1f5e2" />



```
3- CLICK  : 'SAVE'
4- CLICK  : 'Backup Now'
```

<img width="1916" height="512" alt="Screenshot 2025-09-11 154151" src="https://github.com/user-attachments/assets/88a63ff2-777e-467e-857b-0644ef698499" />

```
5- Extract Backup :
```


<img width="704" height="101" alt="Screenshot 2025-09-11 160114" src="https://github.com/user-attachments/assets/b91ce4db-9843-4280-b8f0-32c73aa12d4d" />
<img width="567" height="101" alt="Screenshot 2025-09-11 160135" src="https://github.com/user-attachments/assets/155ce7d8-c2fc-4b54-b054-f7c7550bec82" />

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-j422-qmxp-hv94
- https://nvd.nist.gov/vuln/detail/CVE-2025-66302
- https://github.com/getgrav/grav/commit/ed640a13143c4177af013cf001969ed2c5e197ee
- https://github.com/getgrav/grav
