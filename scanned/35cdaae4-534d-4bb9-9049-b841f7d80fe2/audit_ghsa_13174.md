# [H] OpenRefine vulnerable to arbitrary file read in project import with mysql jdbc url attack

## Summary
Severity: High
Advisory: GHSA-qqh2-wvmv-h72m
CVE: CVE-2023-41886
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-qqh2-wvmv-h72m
Type: github-advisory

## Affected
- Maven: `org.openrefine:database` — affected >=0 <3.7.5

## Details
### Summary
An arbitrary file read vulnerability allows any unauthenticated user to read the file on the server._

### Details
Hi,Team,
i find openrefine support to import data from database,When use mysql jdbc to connect to database,It is vulnerable to jdbc url attacks,for example,unauthenticated attacker can read the file on the server.
There are some differences in utilization depending on the version of the mysql-connector dependency on the server side.  
1.  mysql-connector-java version > 8.14
The default value of `allowLoadLocalInfile` on the server side is false in this case.We need to manually set this value to true in the connection string.  
Since the way to get the databaseurl in `com/google/refine/extension/database/mysql/MySQLConnectionManager.java` is to splice the individual configurations directly, we can set the `allowLoadLocalInfile` parameter after the other parameters(for example the `databaseName` parameter ).  
![image](https://user-images.githubusercontent.com/24366795/262531956-ef8bb163-6692-4494-92f9-3b9bcffdf503.png)  
![image](https://user-images.githubusercontent.com/24366795/262531716-95e7c9a6-601d-4157-bce9-c58d17a6e3ea.png)
![image](https://user-images.githubusercontent.com/24366795/262531614-a34f891f-acd2-4354-bbbe-96447a9dcbd1.png)
2.  mysql-connector-java version <= 8.14
The default value of `allowLoadLocalInfile` on the server side is true in this case.so wo don't need do anything,Just connect to our malicious server.

### PoC
env:   
centos 7
openrefine 3.7.4 
jdk11 
mysql-connector-java version 8.30.0  

you can use the tool https://github.com/4ra1n/mysql-fake-server to running a malicious mysql server.  
![image](https://user-images.githubusercontent.com/24366795/262536594-a62dbc2c-62d2-4b21-a351-5be7f506f852.png)  
for example,to read the /etc/passwd file.
![image](https://user-images.githubusercontent.com/24366795/262539711-f274a396-9c0a-4ace-b3af-3b4e5309ab00.png)
set the `username` to `base64ZmlsZXJlYWRfL2V0Yy9wYXNzd2Q=` and `Database name` to `test?allowLoadLocalInfile=true#` (for  mysql-connector-java version <= 8.14,just setting the database name normally) and test to connect your malicious mysql server.
you can get the file in your fake-server-files directory.
![image](https://user-images.githubusercontent.com/24366795/262542538-c9f501a4-899f-4b57-89b9-b8dd42f535fb.png)


### Impact

An arbitrary file read vulnerability allows any unauthenticated user to read the file on the server._

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-qqh2-wvmv-h72m
- https://nvd.nist.gov/vuln/detail/CVE-2023-41886
- https://github.com/OpenRefine/OpenRefine/commit/2de1439f5be63d9d0e89bbacbd24fa28c8c3e29d
- https://github.com/OpenRefine/OpenRefine
