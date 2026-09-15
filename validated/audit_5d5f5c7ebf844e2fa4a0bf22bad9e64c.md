[1](#0-0) [2](#0-1)

### Citations

**File:** core/web/router.go (L63-72)
```go
	tls := config.WebServer().TLS()
	engine.Use(
		otelgin.Middleware("chainlink-web-routes",
			otelgin.WithTracerProvider(otel.GetTracerProvider())),
		limits.RequestSizeLimiter(config.WebServer().HTTPMaxSize()),
		loggerFunc(app.GetLogger()),
		gin.Recovery(),
		cors,
		secureMiddleware(tls.ForceRedirect(), tls.Host(), config.Insecure().DevWebServer()),
	)
```

**File:** core/services/chainlink/config_web_server.go (L144-146)
```go
func (w *webServerConfig) HTTPMaxSize() int64 {
	return int64(*w.c.HTTPMaxSize)
}
```
