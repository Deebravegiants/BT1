# [?] fix: tools/debug-ui/Dockerfile to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-10-25
Source: https://github.com/near/nearcore/commit/deb131c0ff34091b33e3dd05b814b1ac776c75ce
Type: security-commit

## Details
fix: tools/debug-ui/Dockerfile to reduce vulnerabilities

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-ALPINE315-CURL-3320718
- https://snyk.io/vuln/SNYK-ALPINE315-CURL-5958915
- https://snyk.io/vuln/SNYK-ALPINE315-CURL-5958915
- https://snyk.io/vuln/SNYK-ALPINE315-LIBWEBP-5902238
- https://snyk.io/vuln/SNYK-ALPINE315-NGHTTP2-5964211

## Patch
### tools/debug-ui/Dockerfile
```diff
@@ -12,6 +12,6 @@ RUN npm run build
 
 # Serving does not require npm; simple nginx is good enough; it's just some
 # static files.
-FROM nginx:1.21-alpine
+FROM nginx:1.25.3-alpine
 COPY --from=build /build/build /var/www/html
 COPY nginx.conf /etc/nginx/conf.d/default.conf
```
