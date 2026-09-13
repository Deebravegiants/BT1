# [H] Netty: Missing CertificateID Validation in OCSP Response Allows Replay Attacks

## Summary
Severity: High
Advisory: GHSA-272m-gcwp-mpwg
CVE: CVE-2026-56820
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-272m-gcwp-mpwg
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler-ssl-ocsp` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-handler-ssl-ocsp` — affected >=0 <4.1.136.Final

## Details
### Summary
Netty's OcspClient does not validate that the CertificateID in an OCSP response matches the requested CertificateID. A bad actor can replay a `GOOD` status response issued for an unrelated certificate (by the same CA) to bypass revocation checks for any certificate.

### Details
`io.netty.handler.ssl.ocsp.OcspClient#validateResponse` fails to assert that the CertificateID within the returned `BasicOCSPResp` matches the original certificate being validated.

When `OcspClient.query(...)` executes, it builds an OCSP request using the victim certificate's serial number and issuer hash. It then sends this request and receives a response. While the client verifies the signature of the response against the trusted issuer (or a valid responder chain), it never checks the CertificateID inside the response payload.

A bad actor who has access to any other valid, non-revoked certificate issued by the same CA can obtain a legitimately signed OCSP response indicating that the unrelated certificate is `GOOD`. The bad actor can then return this valid response to the Netty client when it queries the status of any other certificate (e.g., a revoked certificate) issued by the same CA. Because the signature is valid (signed by the CA) and the CertificateID is ignored, the client will incorrectly accept the target certificate as valid.

As per https://datatracker.ietf.org/doc/html/rfc6960#section-3.2 we have:

```
Prior to accepting a signed response for a particular certificate as
   valid, OCSP clients SHALL confirm that:

   1. The certificate identified in a received response corresponds to
      the certificate that was identified in the corresponding request;
```

### PoC
The following test case in `io.netty.handler.ssl.ocsp.OcspClientTest` demonstrates how the implementation accepts a forged OCSP response for a completely unrelated certificate, proving the bypass.

```java
    @Test
    void testCertIdBypass() throws Exception {
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

        X509CertificateHolder caHolder = new JcaX509CertificateHolder(caRoot.getCertificate());
        BasicOCSPResp forgedBasicResp = createBasicOcspResponse(caRoot, new X509CertificateHolder[]{caHolder});
        OCSPResp forgedResponse = new OCSPRespBuilder().build(OCSPRespBuilder.SUCCESSFUL, forgedBasicResp);
        byte[] forgedResponseEncoded = forgedResponse.getEncoded();

        EventLoopGroup group = new MultiThreadIoEventLoopGroup(1, NioIoHandler.newFactory());
        try {
            IoTransport transport = IoTransport.create(group.next(), () -> {
                NioSocketChannel channel = new NioSocketChannel();
                channel.pipeline().addFirst(new ChannelOutboundHandlerAdapter() {
                    @Override
                    public void connect(ChannelHandlerContext ctx, SocketAddress remoteAddress, SocketAddress localAddress, ChannelPromise promise) {
                        promise.setSuccess();

                        ctx.executor().execute(() -> {
                            ctx.pipeline().fireChannelActive();

                            DefaultFullHttpResponse httpResponse = new DefaultFullHttpResponse(
                                    HttpVersion.HTTP_1_1, HttpResponseStatus.OK, Unpooled.wrappedBuffer(forgedResponseEncoded));
                            httpResponse.headers().set(HttpHeaderNames.CONTENT_TYPE, "application/ocsp-response");
                            httpResponse.headers().set(HttpHeaderNames.CONTENT_LENGTH, httpResponse.content().readableBytes());

                            ctx.pipeline().fireChannelRead(httpResponse);
                        });
                    }
                });
                return channel;
            }, NioDatagramChannel::new);

            DnsNameResolver resolver = OcspServerCertificateValidator.createDefaultResolver(transport);
            Promise<BasicOCSPResp> promise = OcspClient.query(targetCert.getCertificate(), caRoot.getCertificate(), false, transport, resolver);

            promise.await();

            assertFalse(promise.isSuccess(),
                    "Netty incorrectly accepted the response for the unrelated certificate. The CertificateID was ignored!");
        } finally {
            group.shutdownGracefully();
        }
    }
```

### Impact
Certificate Validation Bypass. Any application using Netty's OcspClient to check certificate revocation status is impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-272m-gcwp-mpwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-56820
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
