# [H] Netty: Out-of-date OCSP Responses Accepted by OcspServerCertificateValidator

## Summary
Severity: High
Advisory: GHSA-g7hg-vrcf-mvmr
CVE: CVE-2026-56821
CWE: CWE-299
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-g7hg-vrcf-mvmr
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler-ssl-ocsp` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-handler-ssl-ocsp` — affected >=0 <4.1.136.Final

## Details
### Summary
`OcspServerCertificateValidator` flags an out-of-date OCSP response but does not stop processing it, so an expired GOOD response is still reported as `VALID`, letting an on-path attacker replay a stale GOOD response to bypass revocation of a since-revoked certificate.

### Details
In `io.netty.handler.ssl.ocsp.OcspServerCertificateValidator#userEventTriggered` the freshness check has no `return`, so execution falls through and a `VALID` `OcspValidationEvent` is still fired:

```java
                        if (!(current.after(response.getThisUpdate()) &&
                                current.before(response.getNextUpdate()))) {
                            ctx.fireExceptionCaught(new IllegalStateException("OCSP Response is out-of-date"));
                        }
```

Nonce validation is optional and off by default, so freshness is the only replay defense — and it is not enforced. Additionally `getNextUpdate()` may be `null`, making `current.before(null)` throw `NullPointerException`.

https://datatracker.ietf.org/doc/html/rfc6960#section-3.2

```
   5. The time at which the status being indicated is known to be
      correct (thisUpdate) is sufficiently recent;

   6. When available, the time at or before which newer information will
      be available about the status of the certificate (nextUpdate) is
      greater than the current time.
```

### PoC

Add the test below to `io.netty.handler.ssl.ocsp.OcspServerCertificateValidatorTest`

```java
    @Test
    void staleOcspResponseIsRejected() throws Exception {
        X509Bundle caRoot = new CertificateBuilder()
                .algorithm(CertificateBuilder.Algorithm.rsa2048)
                .subject("CN=TrustedRootCA")
                .setIsCertificateAuthority(true)
                .buildSelfSigned();

        GeneralName ocspName = new GeneralName(GeneralName.uniformResourceIdentifier, "http://localhost/");
        AuthorityInformationAccess aia = new AuthorityInformationAccess(
                new AccessDescription(AccessDescription.id_ad_ocsp, ocspName));
        X509Bundle targetCert = new CertificateBuilder()
                .algorithm(CertificateBuilder.Algorithm.rsa2048)
                .subject("CN=TargetServer")
                .addExtensionOctetString("1.3.6.1.5.5.7.1.1", false, aia.getEncoded())
                .buildIssuedBy(caRoot);

        Date past = new Date(System.currentTimeMillis() - TimeUnit.DAYS.toMillis(7));
        CertificateID certId = new CertificateID(
                new JcaDigestCalculatorProviderBuilder().build().get(CertificateID.HASH_SHA1),
                new JcaX509CertificateHolder(caRoot.getCertificate()),
                targetCert.getCertificate().getSerialNumber());
        BasicOCSPRespBuilder respBuilder = new BasicOCSPRespBuilder(
                new RespID(new JcaX509CertificateHolder(caRoot.getCertificate()).getSubject()));
        respBuilder.addResponse(certId, CertificateStatus.GOOD, past, past);
        BasicOCSPResp expiredBasicResp = respBuilder.build(
                new JcaContentSignerBuilder("SHA256withRSA").build(caRoot.getKeyPair().getPrivate()),
                new X509CertificateHolder[0],
                past);
        final byte[] responseEncoded = new OCSPRespBuilder()
                .build(OCSPRespBuilder.SUCCESSFUL, expiredBasicResp).getEncoded();

        IoTransport defaultTransport = createDefaultTransport();
        IoTransport mockTransport = IoTransport.create(defaultTransport.eventLoop(), () -> {
                NioSocketChannel channel = new NioSocketChannel();
                channel.pipeline().addFirst(new ChannelOutboundHandlerAdapter() {
                    @Override
                    public void connect(ChannelHandlerContext ctx, SocketAddress remoteAddress,
                                        SocketAddress localAddress, ChannelPromise promise) {
                        promise.setSuccess();
                        ctx.executor().execute(() -> {
                            ctx.pipeline().fireChannelActive();
                            DefaultFullHttpResponse httpResponse = new DefaultFullHttpResponse(
                                    HttpVersion.HTTP_1_1, HttpResponseStatus.OK,
                                    Unpooled.wrappedBuffer(responseEncoded));
                            httpResponse.headers().set(HttpHeaderNames.CONTENT_TYPE, "application/ocsp-response");
                            httpResponse.headers().set(HttpHeaderNames.CONTENT_LENGTH,
                                    httpResponse.content().readableBytes());
                            ctx.pipeline().fireChannelRead(httpResponse);
                        });
                    }
                });
                return channel;
            }, defaultTransport.datagramChannel());

            SslContext serverSslCtx = SslContextBuilder
                    .forServer(targetCert.getKeyPair().getPrivate(),
                            targetCert.getCertificate(), caRoot.getCertificate())
                    .build();
            Channel serverChannel = new ServerBootstrap()
                    .group(defaultTransport.eventLoop())
                    .channel(NioServerSocketChannel.class)
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ch.pipeline().addLast(serverSslCtx.newHandler(ch.alloc()));
                        }
                    })
                    .bind(0).sync().channel();

            int serverPort = ((InetSocketAddress) serverChannel.localAddress()).getPort();

            AtomicBoolean validEventFired = new AtomicBoolean();
            AtomicReference<Throwable> caughtException = new AtomicReference<>();
            CountDownLatch latch = new CountDownLatch(1);

            DnsNameResolver resolver = OcspServerCertificateValidator.createDefaultResolver(mockTransport);
            SslContext clientSslCtx = SslContextBuilder.forClient()
                    .trustManager(InsecureTrustManagerFactory.INSTANCE)
                    .build();
            new Bootstrap()
                    .group(defaultTransport.eventLoop())
                    .channel(NioSocketChannel.class)
                    .handler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ch.pipeline().addLast(clientSslCtx.newHandler(ch.alloc(), "127.0.0.1", serverPort));
                            ch.pipeline().addLast(
                                    new OcspServerCertificateValidator(true, false, mockTransport, resolver));
                            ch.pipeline().addLast(new ChannelInboundHandlerAdapter() {
                                @Override
                                public void userEventTriggered(ChannelHandlerContext ctx, Object evt) {
                                    if (evt instanceof OcspValidationEvent &&
                                            ((OcspValidationEvent) evt).response().status() ==
                                                    OcspResponse.Status.VALID) {
                                        validEventFired.set(true);
                                    }
                                    ctx.fireUserEventTriggered(evt);
                                }

                                @Override
                                public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
                                    caughtException.compareAndSet(null, cause);
                                    ctx.channel().close();
                                    latch.countDown();
                                }
                            });
                        }
                    })
                    .connect("127.0.0.1", serverPort).sync();

            assertTrue(latch.await(5, TimeUnit.SECONDS));
            assertFalse(validEventFired.get(),
                    "OcspValidationEvent(VALID) must not be emitted for a stale OCSP response");
            assertNotNull(caughtException.get());
            assertInstanceOf(IllegalStateException.class, caughtException.get());

            serverChannel.close().sync();
            resolver.close();
    }
```
### Impact
Certificate revocation bypass via replay of an expired OCSP response. Any application using `OcspServerCertificateValidator` is affected; a revoked certificate can be accepted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-g7hg-vrcf-mvmr
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
