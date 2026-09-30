# [?] fix(security): Fixes vulnerability with golang.org/x/net #125

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2025-01-14
Source: https://github.com/berachain/beacon-kit/commit/dba63d0c4f32ffdeaf37b6382daa31469298fa50
Type: security-commit

## Details
fix(security): Fixes vulnerability with golang.org/x/net #125

## Patch
### go.mod
```diff
@@ -252,7 +252,7 @@ require (
 	go.opentelemetry.io/otel/trace v1.32.0 // indirect
 	golang.org/x/arch v0.12.0 // indirect
 	golang.org/x/exp v0.0.0-20241108190413-2d47ceb2692f // indirect
-	golang.org/x/net v0.32.0 // indirect
+	golang.org/x/net v0.33.0 // indirect
 	golang.org/x/sys v0.28.0 // indirect
 	golang.org/x/term v0.27.0 // indirect
 	golang.org/x/text v0.21.0 // indirect
```

### go.sum
```diff
@@ -790,8 +790,8 @@ golang.org/x/net v0.0.0-20210405180319-a5a99cb37ef4/go.mod h1:p54w0d4576C0XHj96b
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.32.0 h1:ZqPmj8Kzc+Y6e0+skZsuACbx+wzMgo5MQsJh9Qd6aYI=
-golang.org/x/net v0.32.0/go.mod h1:CwU0IoeOlnQQWJ6ioyFrfRuomB8GKF6KbYXZVyeXNfs=
+golang.org/x/net v0.33.0 h1:74SYHlV8BIgHIFC/LrYkOGIwL19eTYXQ5wc6TBuO36I=
+golang.org/x/net v0.33.0/go.mod h1:HXLR5J+9DxmrqMwG9qjGCxZ+zKXxBru04zlTvWlWuN4=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20200107190931-bf48bf16ab8d/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.24.0 h1:KTBBxWqUa0ykRPLtV69rRto9TLXcqYkeswu48x/gvNE=
```
