# [?] cmd/puppeth: fix dashboard crash caused by updated base image

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-07-06
Source: https://github.com/ethereum/go-ethereum/commit/78c34fdc3c44770b121f8f430d0b00c629e4e091
Type: security-commit

## Details
cmd/puppeth: fix dashboard crash caused by updated base image

## Patch
### cmd/puppeth/module_dashboard.go
```diff
@@ -482,7 +482,7 @@ ADD puppeth.png /dashboard/puppeth.png
 
 EXPOSE 80
 
-CMD ["node", "/server.js"]
+CMD ["node", "./server.js"]
 `
 
 // dashboardComposefile is the docker-compose.yml file required to deploy and
```
