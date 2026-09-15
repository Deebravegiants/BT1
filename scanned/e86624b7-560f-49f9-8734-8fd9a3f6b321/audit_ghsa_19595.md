# [M] Minio Operator uses Kubernetes apiserver audience for AssumeRoleWithWebIdentity STS

## Summary
Severity: Medium
Advisory: GHSA-7m6v-q233-q9j9
CVE: CVE-2025-32963
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-7m6v-q233-q9j9
Type: github-advisory

## Affected
- Go: `github.com/minio/operator` — affected >=0 <7.1.0

## Details
# Prevent token leakage / privilege escalation

## MinIO Operator STS: A Quick Overview

MinIO Operator STS is a native IAM Authentication for Kubernetes. MinIO Operator offers support for [Secure Tokens](https://min.io/docs/minio/linux/developers/security-token-service.html?ref=op-gh) (a.k.a. STS) which are a form of temporary access credentials for your MinIO Tenant. In essence, this allows you to control access to your MinIO tenant from your applications without having to explicitly create credentials for each application.

For an application to gain access into a MinIO Tenant, a `PolicyBinding` resource is required, granting explicit access to the applications by validating the kubernetes [Service Account](https://kubernetes.io/docs/concepts/security/service-accounts/) authorization token. 

The service account token is validated as follows:

1. The application calls `AssumeRoleWithWebIdentity` API MinIO Operator provides.
2. MinIO Operator verifies the Service Account token agains the kubernetes API using the [TokenReview API](https://kubernetes.io/docs/reference/kubernetes-api/authentication-resources/token-review-v1/)
3. MinIO Operator reviews the TokenReviewResult confirms if the token is a valid token and the user is authenticated.
4. MinIO Operator validates the service account has `PolicyBinding` in the Tenant namespace.
5. MinIO Operator gets the PolicyBinding
6. MinIO Operator calls the AssumeRole API in the MinIO Tenant
7. MinIO Operator obtains temporary credentials (STS).
8. MinIO Operator return temporary Credentials to the requester application.
9. The applicaiton consumes Object Storage using the temporary credentials.

![STS Diagram](https://raw.githubusercontent.com/minio/operator/master/docs/images/sts-diagram.png)

## Understanding Audiences in Kubernetes TokenReview

In step 2 the `TokenReview` API call attempts to authenticate a token to a known user, TokenReviewStatus is the result of the `TokenReview` request.

Audiences are audience identifiers chosen by the authenticator that are compatible with both the TokenReview and token. 

An identifier is any identifier in the intersection of the TokenReviewSpec audiences and the token's audiences.

A client of the TokenReview API that sets the `spec.audiences` field should validate that a compatible audience identifier is returned in the status.audiences field to ensure that the TokenReview server is audience aware. 
**If no audiences are provided, the audience will default to the audience of the Kubernetes apiserver.**

## Solution: Properly Issuing and Using Audience-Specific ServiceAccount Tokens

This PR ensures the Operator STS service request the Service Account JWT to belong to the audience`sts.min.io` in the TokenReviewRequest.

This PR ensures the examples and documentation provided guides in how to create Service accounts with "disabled auto mount services tokens", by doing this the pods where the service account is used no longer mounts the service account automatically in the path `/var/run/secrets/kubernetes.io/serviceaccount`.

For illustrative purposes, here is how you disable auto mount of service account tokens at the service account level.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  namespace: namespace-name
  name: service-account name
automountServiceAccountToken: false
```

Additionally documentation and examples show how to request an audience-specific token with audience `sts.min.io`, by asking for an ServiceAccount Token to be audience specific.

For illustrative purposes, here is how you request an audience specific service account token in a pod:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: job-name
  namespace: job-namespace
spec:
  template:
    spec:
      serviceAccountName: service-account-name
      volumes:
        - name: sa-token
          projected:
            sources:
              - serviceAccountToken:
                  audience: "sts.min.io"
                  expirationSeconds: 86400
                  path: token
      containers:
        - name: mc
...
          volumeMounts:
            - name: sa-token
              mountPath: /var/run/secrets/sts.min.io/serviceaccount
              readOnly: true
```

### How this prevent a token leakage or possible privilege escalation?.

This setup prevents privilege escalation and token leakage by combining multiple defense-in-depth mechanisms that ensure service account tokens are only usable by their intended audience, short-lived, and not exposed unnecessarily.

#### Audience restriction (aud: sts.min.io)

**Problem**: A ServiceAccount token is often valid for multiple audiences (e.g., the default Kubernetes API server). Without scoping, it can be replayed to other internal systems, which may unintentionally trust it.

**Mitigation**: Now we enforce that tokens are explicitly created for the sts.min.io audience using the Kubernetes TokenRequest API, and the MinIO Operator:

Sends audiences: ["sts.min.io"] in the TokenReview.

Verifies that the token was issued with this audience via status.audiences.

**Effect**: Even if a token is stolen or misused, it will fail validation if used outside the sts.min.io STS endpoint (e.g., reused at the API server or another service).

#### Token Leakage Mitigation

Disabling auto-mounted service account tokens

**Problem**: By default, Kubernetes mounts long-lived service account tokens into all pods at `/var/run/secrets/kubernetes.io/serviceaccount`, making them vulnerable to theft if the container is compromised.

**Mitigation**:  No we guide users to set `automountServiceAccountToken: false` in their ServiceAccount definitions.

**Effect**: Prevents automatic token injection into all pods, reducing the attack surface.

####  Requesting short-lived, audience-specific tokens via serviceAccountToken projection

**Problem**: Long-lived tokens can be reused indefinitely if leaked.
**Mitigation**: You use projected service account tokens with: 
- audience: "sts.min.io"
- A short expirationSeconds (e.g., 86400 = 24 hours, or even shorter)

**Effect**: Even if the token is leaked, it is:

- Only usable for sts.min.io
- Short-lived and expires soon
- Revocable by disabling the SA or STS access

## Affected Versions and Risk Assessment
The issue affects MinIO Operator versions v5.0.x and above, when the STS feature was first introduced.

* In v5.0.x, STS was introduced as v1alpha1 and disabled by default. It required explicit API calls to be used.
* In v6.0.x, STS graduated to v1beta1 and was enabled by default, but still requires explicit calls to the STS API for token usage.

The risk is minimal, as:

* The Operator does not persist the token (neither in memory nor on disk).
* The Operator only uses the token for a single validation and does not reuse it for any other purpose.

# Release
Fix released in [v7.1.0](https://github.com/minio/operator/releases/tag/v7.1.0)

## References
- https://github.com/minio/operator/security/advisories/GHSA-7m6v-q233-q9j9
- https://nvd.nist.gov/vuln/detail/CVE-2025-32963
- https://github.com/minio/operator/commit/d586294d526bf0d8e6097225114655f68b0adcc5
- https://github.com/minio/operator
- https://github.com/minio/operator/releases/tag/v7.1.0
