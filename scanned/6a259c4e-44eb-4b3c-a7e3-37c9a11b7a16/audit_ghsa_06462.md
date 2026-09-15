# [H] Netty: TOCTOU in OcspServerCertificateValidator

## Summary
Severity: High
Advisory: GHSA-wc96-39fc-566f
CVE: CVE-2026-56822
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-wc96-39fc-566f
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler-ssl-ocsp` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-handler-ssl-ocsp` — affected >=0 <4.1.136.Final

## Details
### Summary
Netty's OcspServerCertificateValidator forwards the SslHandshakeCompletionEvent before the asynchronous OCSP validation completes. This allows the client's downstream handlers to send sensitive application data (e.g., HTTP requests) to a revoked server before the channel is closed by the OCSP check.

### Details
In `io.netty.handler.ssl.ocsp.OcspServerCertificateValidator#userEventTriggered`, when an `SslHandshakeCompletionEvent` is received, the validator immediately calls `ctx.fireUserEventTriggered(evt)`. It then initiates an asynchronous OCSP query using `OcspClient.query`.

Because the handshake completion event is forwarded immediately, downstream handlers in the client's pipeline are notified that the TLS handshake is successful. They may then begin reading and processing incoming application data or sending outgoing data. If the OCSP response later indicates the server's certificate is REVOKED, the validator closes the channel, but by this time, the client may have already leaked sensitive data to a revoked server or processed malicious responses from it.

### PoC

```java
    @Test
    public void test() throws Exception {
        EventLoopGroup group = new MultiThreadIoEventLoopGroup(NioIoHandler.newFactory());
        try {
            OCSPRespBuilder respBuilder = new OCSPRespBuilder();
            OCSPResp response = respBuilder.build(OCSPRespBuilder.INTERNAL_ERROR, null);
            byte[] responseEncoded = response.getEncoded();

            IoTransport mockTransport = IoTransport.create(group.next(), () -> {
                NioSocketChannel channel = new NioSocketChannel();
                channel.pipeline().addFirst(new ChannelOutboundHandlerAdapter() {
                    @Override
                    public void connect(ChannelHandlerContext ctx, SocketAddress remoteAddress, SocketAddress localAddress, ChannelPromise promise) {
                        promise.setSuccess();

                        ctx.executor().schedule(() -> {
                            ctx.pipeline().fireChannelActive();

                            DefaultFullHttpResponse httpResponse = new DefaultFullHttpResponse(
                                    HttpVersion.HTTP_1_1, HttpResponseStatus.OK, Unpooled.wrappedBuffer(responseEncoded));
                            httpResponse.headers().set(HttpHeaderNames.CONTENT_TYPE, "application/ocsp-response");
                            httpResponse.headers().set(HttpHeaderNames.CONTENT_LENGTH, httpResponse.content().readableBytes());

                            ctx.pipeline().fireChannelRead(httpResponse);
                        }, 500, TimeUnit.MILLISECONDS);
                    }
                });
                return channel;
            }, NioDatagramChannel::new);

            X509Bundle caRoot = new CertificateBuilder()
                    .algorithm(CertificateBuilder.Algorithm.rsa2048)
                    .subject("CN=TrustedRootCA")
                    .setIsCertificateAuthority(true)
                    .buildSelfSigned();

            GeneralName ocspName = new GeneralName(GeneralName.uniformResourceIdentifier, "http://localhost/");
            AuthorityInformationAccess aia = new AuthorityInformationAccess(new AccessDescription(AccessDescription.id_ad_ocsp, ocspName));
            X509Bundle targetCert = new CertificateBuilder()
                    .algorithm(CertificateBuilder.Algorithm.rsa2048)
                    .subject("CN=TargetServer")
                    .addExtensionOctetString("1.3.6.1.5.5.7.1.1", false, aia.getEncoded())
                    .buildIssuedBy(caRoot);

            SslContext serverSslCtx = SslContextBuilder.forServer(targetCert.getKeyPair().getPrivate(), targetCert.getCertificate()).build();

            CopyOnWriteArrayList<String> receivedData = new CopyOnWriteArrayList<>();
            CountDownLatch dataReceivedLatch = new CountDownLatch(1);

            new ServerBootstrap()
                    .group(group)
                    .channel(NioServerSocketChannel.class)
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ch.pipeline().addLast(serverSslCtx.newHandler(ch.alloc()));
                            ch.pipeline().addLast(new SimpleChannelInboundHandler<ByteBuf>() {
                                @Override
                                protected void channelRead0(ChannelHandlerContext ctx, ByteBuf msg) {
                                    receivedData.add(msg.toString(CharsetUtil.UTF_8));
                                    dataReceivedLatch.countDown();
                                }
                            });
                        }
                    })
                    .bind(8080)
                    .sync()
                    .channel();

            SslContext clientSslCtx = SslContextBuilder.forClient()
                    .trustManager(InsecureTrustManagerFactory.INSTANCE)
                    .build();

            DnsNameResolver resolver = OcspServerCertificateValidator.createDefaultResolver(mockTransport);
            Channel clientChannel = new Bootstrap()
                    .group(group)
                    .channel(NioSocketChannel.class)
                    .handler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ch.pipeline().addLast(clientSslCtx.newHandler(ch.alloc(), "127.0.0.1", 8080));
                            ch.pipeline().addLast(new OcspServerCertificateValidator(true, false, mockTransport, resolver));
                            ch.pipeline().addLast(new ChannelInboundHandlerAdapter() {
                                @Override
                                public void userEventTriggered(ChannelHandlerContext ctx, Object evt) {
                                    if (evt instanceof SslHandshakeCompletionEvent) {
                                        SslHandshakeCompletionEvent sslEvent = (SslHandshakeCompletionEvent) evt;
                                        if (sslEvent.isSuccess()) {
                                            ctx.writeAndFlush(Unpooled.copiedBuffer("SECRET_DATA", CharsetUtil.UTF_8));
                                        }
                                    }
                                    ctx.fireUserEventTriggered(evt);
                                }
                            });
                        }
                    })
                    .connect("127.0.0.1", 8080)
                    .sync()
                    .channel();

            assertTrue(clientChannel.closeFuture().await(5, TimeUnit.SECONDS));

            Thread.sleep(200);

            assertFalse(receivedData.contains("SECRET_DATA"), "Server should not receive the data.");
        } finally {
            group.shutdownGracefully();
        }
    }
```

### Impact
TOCTOU. Client applications relying on OcspServerCertificateValidator to enforce server certificate revocation are impacted. A malicious server with a revoked certificate can successfully establish a TLS connection and receive sensitive application data from the client (or send malicious data to it) during the window between the TLS handshake completing and the asynchronous OCSP check failing.

## References
- https://github.com/netty/netty/security/advisories/GHSA-wc96-39fc-566f
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
