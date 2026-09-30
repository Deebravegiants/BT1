# [?] fix: int overflow for 32 bit machines (#2135)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2023-07-20
Source: https://github.com/celestiaorg/celestia-app/commit/9278736e0b3f4a760eaf9075c47e779e42057dce
Type: security-commit

## Details
fix: int overflow for 32 bit machines (#2135)

Closes https://github.com/celestiaorg/celestia-app/issues/2129

https://github.com/celestiaorg/celestia-app/pull/2121 didn't actually
fix the issue because the expression

```go
NanosecondsPerYear = int64(NanosecondsPerSecond * SecondsPerYear)
```
was multiplying two `int`s together prior to the cast to `int64`. Since
the product of those two `int`s overflows an `int32`, the value would
overflow prior to the cast.

The fix proposed in this PR converts SecondsPerYear to an `int64`. Now
the expression multiplies an `int` and `int64` so the product is an
`int64` which won't overflow.

## Testing

I added this to the Makefile

```go
## build-arm: Build the celestia-appd binary into the ./build directory. Target the linux OS and ARM (32-bit) architecture.
build-arm: mod
	@cd ./cmd/celestia-appd
	@mkdir -p build/
	@GOOS=linux GOARCH=arm go build $(BUILD_FLAGS) -o build/ ./cmd/celestia-appd
	@go mod tidy -compat=1.20
.PHONY: build-arm
```

Before

```shell
$ make build-arm
--> Updating go.mod
# github.com/celestiaorg/celestia-app/x/mint/types
x/mint/types/constants.go:15:29: NanosecondsPerSecond * SecondsPerYear (constant 31556952000000000 of type int) overflows int
make: *** [build-arm] Error 1
```

After

```shell
$ make build-arm
--> Updating go.mod
```

## Patch
### x/mint/types/constants.go
```diff
@@ -11,8 +11,8 @@ const (
 	// value isn't 365 because 97 out of 400 years are leap years. See
 	// https://en.wikipedia.org/wiki/Year
 	DaysPerYear        = 365.2425
-	SecondsPerYear     = int(SecondsPerMinute * MinutesPerHour * HoursPerDay * DaysPerYear) // 31,556,952
-	NanosecondsPerYear = int64(NanosecondsPerSecond * SecondsPerYear)                       // 31,556,952,000,000,000
+	SecondsPerYear     = int64(SecondsPerMinute * MinutesPerHour * HoursPerDay * DaysPerYear) // 31,556,952
+	NanosecondsPerYear = int64(NanosecondsPerSecond * SecondsPerYear)                         // 31,556,952,000,000,000
 
 	InitialInflationRate = 0.08
 	DisinflationRate     = 0.1
```
