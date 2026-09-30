# [?] fix: missing env var causing pg crash on startup (#3511)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-05-05
Source: https://github.com/graphprotocol/graph-node/commit/758ec74b138496ef347d1fe6f71567f63bb8b58e
Type: security-commit

## Details
fix: missing env var causing pg crash on startup (#3511)

## Patch
### docker/docker-compose.yml
```diff
@@ -40,5 +40,6 @@ services:
       POSTGRES_USER: graph-node
       POSTGRES_PASSWORD: let-me-in
       POSTGRES_DB: graph-node
+      PGDATA: "/data/postgres"
     volumes:
       - ./data/postgres:/var/lib/postgresql/data
```
