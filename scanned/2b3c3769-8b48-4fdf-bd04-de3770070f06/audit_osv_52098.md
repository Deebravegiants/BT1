# [H] CVE-2021-47068

## Summary
Severity: High
Advisory: CVE-2021-47068
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47068
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/nfc: fix use-after-free llcp_sock_bind/connect

Commits 8a4cd82d ("nfc: fix refcount leak in llcp_sock_connect()")
and c33b1cc62 ("nfc: fix refcount leak in llcp_sock_bind()")
fixed a refcount leak bug in bind/connect but introduced a
use-after-free if the same local is assigned to 2 different sockets.

This can be triggered by the following simple program:
    int sock1 = socket( AF_NFC, SOCK_STREAM, NFC_SOCKPROTO_LLCP );
    int sock2 = socket( AF_NFC, SOCK_STREAM, NFC_SOCKPROTO_LLCP );
    memset( &addr, 0, sizeof(struct sockaddr_nfc_llcp) );
    addr.sa_family = AF_NFC;
    addr.nfc_protocol = NFC_PROTO_NFC_DEP;
    bind( sock1, (struct sockaddr*) &addr, sizeof(struct sockaddr_nfc_llcp) )
    bind( sock2, (struct sockaddr*) &addr, sizeof(struct sockaddr_nfc_llcp) )
    close(sock1);
    close(sock2);

Fix this by assigning NULL to llcp_sock->local after calling
nfc_llcp_local_put.

This addresses CVE-2021-23134.

## References
- https://git.kernel.org/stable/c/18175fe17ae043a0b81e5d511f8817825784c299
- https://git.kernel.org/stable/c/18ae4a192a4496e48a5490b52812645d2413307c
- https://git.kernel.org/stable/c/48fba458fe54cc2a980a05c13e6c19b8b2cfb610
- https://git.kernel.org/stable/c/c61760e6940dd4039a7f5e84a6afc9cdbf4d82b6
- https://git.kernel.org/stable/c/ccddad6dd28530e716448e594c9ca7c76ccd0570
- https://git.kernel.org/stable/c/e32352070bcac22be6ed8ab635debc280bb65b8c
- https://git.kernel.org/stable/c/26157c82ba756767b2bd66d28a71b1bc454447f6
- https://git.kernel.org/stable/c/374cdde4dcc9c909a60713abdbbf96d5e3e09f91
- https://git.kernel.org/stable/c/6b7021ed36dabf29e56842e3408781cd3b82ef6e
