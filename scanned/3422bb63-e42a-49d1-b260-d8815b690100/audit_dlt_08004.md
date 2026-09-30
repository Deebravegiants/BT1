# [?] feat(test): add jetty test for CVE-2023-40167  (#5600)

## Summary
Severity: Unknown
Chain: Tron
Component: tronprotocol/java-tron
Published: 2023-11-29
Source: https://github.com/tronprotocol/java-tron/commit/a66316c4aa632fd9237e6ed77a972b23b46271c7
Type: security-commit

## Details
feat(test): add jetty test for CVE-2023-40167  (#5600)

Co-authored-by: morgan.peng <morgan.p@qq.com>

## Patch
### framework/src/test/java/org/tron/common/jetty/JettyServerTest.java
```diff
@@ -0,0 +1,63 @@
+package org.tron.common.jetty;
+
+import java.net.URI;
+import lombok.extern.slf4j.Slf4j;
+import org.apache.http.HttpResponse;
+import org.apache.http.client.HttpClient;
+import org.apache.http.client.methods.HttpGet;
+import org.apache.http.impl.client.DefaultHttpClient;
+import org.eclipse.jetty.server.Server;
+import org.eclipse.jetty.server.ServerConnector;
+import org.eclipse.jetty.servlet.DefaultServlet;
+import org.eclipse.jetty.servlet.ServletContextHandler;
+import org.eclipse.jetty.servlet.ServletHolder;
+import org.junit.AfterClass;
+import org.junit.Assert;
+import org.junit.BeforeClass;
+import org.junit.Test;
+
+@Slf4j
+public class JettyServerTest {
+  private static Server server;
+  private static URI serverUri;
+
+  @BeforeClass
+  public static void startJetty() throws Exception {
+    server = new Server();
+    ServerConnector connector = new ServerConnector(server);
+    connector.setPort(0);
+    server.addConnector(connector);
+
+    ServletContextHandler context = new ServletContextHandler();
+    ServletHolder defaultServ = new ServletHolder("default", DefaultServlet.class);
+    context.addServlet(defaultServ, "/");
+    server.setHandler(context);
+    server.start();
+    String host = connector.getHost();
+    if (host == null) {
+      host = "localhost";
+    }
+    int port = connector.getLocalPort();
+    serverUri = new URI(String.format("http://%s:%d/", host, port));
+  }
+
+  @AfterClass
+  public static void stopJetty() {
+    try {
+      server.stop();
+    } catch (Exception e) {
+      throw new RuntimeException(e);
+    }
+  }
+
+  @Test
+  public void testGet() throws Exception {
+    HttpClient client = new DefaultHttpClient();
+    HttpGet request = new HttpGet(serverUri.resolve("/"));
+    request.setHeader("Content-Length", "+450");
+    HttpResponse mockResponse = client.execute(request);
+    Assert.assertTrue(mockResponse.getStatusLine().toString().contains(
+        "400 Invalid Content-Length Value"));
+  }
+
+}
```
