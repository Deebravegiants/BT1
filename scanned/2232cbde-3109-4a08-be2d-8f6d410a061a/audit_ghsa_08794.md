# [H] Argo vulnerable to exposure of artifact repository credentials

## Summary
Severity: High
Advisory: GHSA-7vf8-2cr6-54mf
CVE: CVE-2026-42295
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-7vf8-2cr6-54mf
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v4` — affected >=4.0.0 <4.0.5

## Details
### Summary
The workflow executor logs all artifact repository credentials (S3 access keys, secret keys, GCS service account keys, Azure account keys, Git passwords, etc.) in plaintext on artifact operation. Any user with read access to workflow pod logs can extract these credentials.

**Note:** This is an incomplete fix of [CVE-2025-62157](https://github.com/argoproj/argo-workflows/security/advisories/GHSA-c2hv-4pfj-mm2r)
### Details
The logging driver passes the entire ArtifactDriver struct to the structured logger, for example:
https://github.com/argoproj/argo-workflows/blob/59f1089b9875723ddffd524513e6bd5cb37e5e31/workflow/artifacts/logging/driver.go#L24

Exposed credential fields:
- S3 (workflow/artifacts/s3/s3.go): AccessKey, SecretKey, SessionToken, ServerSideCustomerKey
- OSS (workflow/artifacts/oss/oss.go): AccessKey, SecretKey, SecurityToken
- GCS (workflow/artifacts/gcs/gcs.go): ServiceAccountKey

### PoC
1. Create template
```yml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: cred-leak-test
  namespace: argo
spec:
  entrypoint: main
  templates:
  - name: main
    container:
      image: alpine:3.13
      command: [sh, -c]
      args: ["echo 'hello' > /tmp/output.txt"]
    outputs:
      artifacts:
      - name: output
        path: /tmp/output.txt
        s3:
          endpoint: minio:9000
          insecure: true
          bucket: my-bucket
          key: test-output.txt
          accessKeySecret:
            name: my-minio-cred
            key: accesskey
          secretKeySecret:
            name: my-minio-cred
            key: secretkey
```

2. Then check the logs
`kubectl -n argo logs "cred-leak-test" -c wait`
<img width="1248" height="322" alt="image" src="https://github.com/user-attachments/assets/a5cf6d66-7d67-408d-8583-27d11ecf1507" />


### Impact
Any user with Kubernetes RBAC permissions to read pod logs in the workflow namespace can extract artifact repository credentials.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-7vf8-2cr6-54mf
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-c2hv-4pfj-mm2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42295
- https://github.com/argoproj/argo-workflows/commit/bdd40908580f727c590c8743836e338b04fe4a87
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/blob/59f1089b9875723ddffd524513e6bd5cb37e5e31/workflow/artifacts/logging/driver.go#L24
- https://github.com/argoproj/argo-workflows/releases/tag/v4.0.5
