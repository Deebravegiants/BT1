# [H] OpenRefine JDBC Attack Vulnerability

## Summary
Severity: High
Advisory: GHSA-6p92-qfqf-qwx4
CVE: CVE-2024-23833
CWE: CWE-22, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-02-12
Source: https://github.com/advisories/GHSA-6p92-qfqf-qwx4
Type: github-advisory

## Affected
- Maven: `org.openrefine:database` — affected >=0 <3.7.8

## Details
### Summary
A jdbc attack vulnerability exists in OpenRefine(version<=3.7.7)

### Details
#### Vulnerability Recurrence
Start by constructing a malicious MySQL Server (using the open source project MySQL_Fake_Server here).
![image](https://user-images.githubusercontent.com/31120718/296241211-96c6a647-8572-4859-837d-dac3d3f52ab0.png)
Then go to the Jdbc connection trigger vulnerability
![image](https://user-images.githubusercontent.com/31120718/296241309-af2c404d-0651-4d4b-86d6-8111cef0295b.png)
#### Vulnerability Analysis
This vulnerability is the bypass of `CVE-2023-41887` vulnerability repair, the main vulnerability principle is actually the use of official syntax features, as shown in the following figure, when the connection we can perform parameter configuration in the Host part
![image](https://user-images.githubusercontent.com/31120718/296241439-db45840c-e3bd-4047-b1ac-499f7aeb4848.png)
In `com.google.refine.extension.database.mysql.MySQLConnectionManager#getConnection` method in the final JdbcUrl structure
![image](https://user-images.githubusercontent.com/31120718/296241473-fc63b0a9-6ecf-47a0-ac7d-d68d833c7c27.png)
That is, in the ` toURI` method call here, you can see that the Host part is directly concatenated for any verification, which can be bypassed using the address feature of mysql
![image](https://user-images.githubusercontent.com/31120718/296241511-e27ba08c-500a-4ed5-b662-96e5e4a8af5f.png)
That is, in the toURI method call here, you can see that the Host part is directly concatenated for any verification, which can be bypassed using the address feature of mysql
![image](https://user-images.githubusercontent.com/31120718/296241733-83d6d0a5-197c-4bcf-835e-0c54b4b8b80f.png)



### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._
```
Type: MySQL
Host: 127.0.0.1:3306,(host=127.0.0.1,port=3306,autoDeserialize=true,allowLoadLocalInfile=true,allowUrlInLocalInfile=true,allowLoadLocalInfileInPath=true),127.0.0.1
Port: 3306
User: win_hosts
Database: test
```


### Impact 
Due to the newer MySQL driver library in the latest version of OpenRefine (8.0.30), there is no associated deserialization utilization point, so original code execution cannot be achieved, but attackers can use this vulnerability to read sensitive files on the target server.

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-6p92-qfqf-qwx4
- https://nvd.nist.gov/vuln/detail/CVE-2024-23833
- https://github.com/OpenRefine/OpenRefine/commit/41ccf574847d856e22488a7c0987ad8efa12a84a
- https://github.com/OpenRefine/OpenRefine
