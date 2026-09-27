# [M] HTTP/2 Stream Cancellation Attack

## Summary
Severity: Medium
Advisory: GHSA-qppj-fm5r-hxr3
CVE: CVE-2023-44487
CWE: CWE-400
Ecosystem: Go, Maven, SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L/E:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-qppj-fm5r-hxr3
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-http2` — affected >=0 <1.28.0
- Go: `golang.org/x/net` — affected >=0 <0.17.0
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=11.0.0-M1 <11.0.0-M12
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.0.0 <10.1.14
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0 <9.0.81
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.0 <8.5.94
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.0-M12
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.0.0 <10.1.14
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0 <9.0.81
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.94
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=9.3.0 <9.4.53
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=10.0.0 <10.0.17
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=11.0.0 <11.0.17
- Maven: `org.eclipse.jetty.http2:http2-server` — affected >=9.3.0 <9.4.53
- Maven: `org.eclipse.jetty.http2:http2-server` — affected >=10.0.0 <10.0.17
- Maven: `org.eclipse.jetty.http2:http2-server` — affected >=11.0.0 <11.0.17
- Maven: `org.eclipse.jetty.http2:jetty-http2-common` — affected >=12.0.0 <12.0.2
- Maven: `org.eclipse.jetty.http2:jetty-http2-server` — affected >=12.0.0 <12.0.2
- Maven: `com.typesafe.akka:akka-http-core` — affected >=0 <10.5.3
- Maven: `com.typesafe.akka:akka-http-core_2.13` — affected >=0 <10.5.3
- Maven: `com.typesafe.akka:akka-http-core_2.12` — affected >=0 <10.5.3
- Maven: `com.typesafe.akka:akka-http-core_2.11` — affected >=0

## Details
## HTTP/2 Rapid reset attack
The HTTP/2 protocol allows clients to indicate to the server that a previous stream should be canceled by sending a RST_STREAM frame. The protocol does not require the client and server to coordinate the cancellation in any way, the client may do it unilaterally. The client may also assume that the cancellation will take effect immediately when the server receives the RST_STREAM frame, before any other data from that TCP connection is processed.

Abuse of this feature is called a Rapid Reset attack because it relies on the ability for an endpoint to send a RST_STREAM frame immediately after sending a request frame, which makes the other endpoint start working and then rapidly resets the request. The request is canceled, but leaves the HTTP/2 connection open. 

The HTTP/2 Rapid Reset attack built on this capability is simple: The client opens a large number of streams at once as in the standard HTTP/2 attack, but rather than waiting for a response to each request stream from the server or proxy, the client cancels each request immediately.

The ability to reset streams immediately allows each connection to have an indefinite number of requests in flight. By explicitly canceling the requests, the attacker never exceeds the limit on the number of concurrent open streams. The number of in-flight requests is no longer dependent on the round-trip time (RTT), but only on the available network bandwidth.

In a typical HTTP/2 server implementation, the server will still have to do significant amounts of work for canceled requests, such as allocating new stream data structures, parsing the query and doing header decompression, and mapping the URL to a resource. For reverse proxy implementations, the request may be proxied to the backend server before the RST_STREAM frame is processed. The client on the other hand paid almost no costs for sending the requests. This creates an exploitable cost asymmetry between the server and the client.

Multiple software artifacts implementing HTTP/2 are affected. This advisory was originally ingested from the `swift-nio-http2` repo advisory and their original conent follows.

## swift-nio-http2 specific advisory
swift-nio-http2 is vulnerable to a denial-of-service vulnerability in which a malicious client can create and then reset a large number of HTTP/2 streams in a short period of time. This causes swift-nio-http2 to commit to a large amount of expensive work which it then throws away, including creating entirely new `Channel`s to serve the traffic. This can easily overwhelm an `EventLoop` and prevent it from making forward progress.

swift-nio-http2 1.28 contains a remediation for this issue that applies reset counter using a sliding window. This constrains the number of stream resets that may occur in a given window of time. Clients violating this limit will have their connections torn down. This allows clients to continue to cancel streams for legitimate reasons, while constraining malicious actors.

## References
- https://github.com/apple/swift-nio-http2/security/advisories/GHSA-qppj-fm5r-hxr3
- https://github.com/h2o/h2o/security/advisories/GHSA-2m7v-gc89-fjqf
- https://nvd.nist.gov/vuln/detail/CVE-2023-44487
- https://github.com/alibaba/tengine/issues/1872
- https://github.com/apache/apisix/issues/10320
- https://github.com/akka/akka-http/issues/4323
- https://github.com/varnishcache/varnish-cache/issues/3996
- https://github.com/tempesta-tech/tempesta/issues/1986
- https://github.com/Azure/AKS/issues/3947
- https://github.com/opensearch-project/data-prepper/issues/3474
- https://github.com/caddyserver/caddy/issues/5877
- https://github.com/openresty/openresty/issues/930
- https://github.com/dotnet/announcements/issues/277
- https://github.com/eclipse/jetty.project/issues/10679
- https://github.com/etcd-io/etcd/issues/16740
- https://github.com/golang/go/issues/63417
- https://github.com/ninenines/cowboy/issues/1615
- https://github.com/haproxy/haproxy/issues/2312
- https://github.com/hyperium/hyper/issues/3337
- https://github.com/kazu-yamamoto/http2/issues/93
