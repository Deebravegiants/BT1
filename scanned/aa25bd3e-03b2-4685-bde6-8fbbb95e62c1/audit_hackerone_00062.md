# [H] RCE  on ingress-nginx-controller via Ingress spec.rules.http.paths.path field

## Summary
Severity: High (CVSS 8.8)
Program: Kubernetes
Weakness: Code Injection
Reporter: ginoah
State: resolved
Disclosed: 2023-10-26T10:07:49.100Z
Source: https://hackerone.com/reports/1620702

## Details
Report Submission Form

## Summary:

A user with ingress create/update privilege may inject config into `nginx.conf` with `path`.
Config the log_format and access_log to write arbitrary file.
Include the file we created to bypass `path` sanitizer to RCE.

## Kubernetes Version:

```
serverVersion:
  buildDate: "2022-03-06T21:32:53Z"
  compiler: gc
  gitCommit: e6c093d87ea4cbb530a7b2ae91e54c0842d8308a
  gitTreeState: clean
  gitVersion: v1.23.4
  goVersion: go1.17.7
  major: "1"
  minor: "23"
  platform: linux/amd64
```

## Component Version:

```
-------------------------------------------------------------------------------
NGINX Ingress controller
  Release:       v1.2.1
  Build:         08848d69e0c83992c89da18e70ea708752f21d7a
  Repository:    https://github.com/kubernetes/ingress-nginx
  nginx version: nginx/1.19.10

-------------------------------------------------------------------------------
```

## Steps To Reproduce:


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1620702_
