### Title
Cross-tenant webhook forgery via `shop-domain` and `topic` headers unauthenticated by HMAC - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (tenant identity) and `topic` (handler-dispatch key) values used afterward are read from unauthenticated headers that the signature never covers.

### Finding Description
`ShopifyAPI::Webhooks::Request` mixes in `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body`: [1](#0-0) 
Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates only the body's HMAC, then uses the unauthenticated `request.topic` to select the handler and the unauthenticated `request.shop` to populate `WebhookMetadata` that the handler uses to identify the tenant: [3](#0-2) 

This is the same bug class as the referenced report: a field that is acted upon (tenant/shop identity, dispatch topic) is not covered by the same integrity check (HMAC) that gates the request. The binding that should hold is:
`HMAC-verified(raw_body) == fields-trusted-for-authorization(shop, topic)`, but the implementation only enforces `HMAC-verified(raw_body)` while `shop`/`topic` are read independently from headers.

### Impact Explanation
Because the shop domain is not bound to the HMAC, a party who legitimately receives a validly-signed webhook for their own store (e.g., by installing the app on their own shop and capturing a real `shopify-hmac-sha256` + body pair) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting a different `shopify-shop-domain` header. `HmacValidator.validate` will still pass because it only recomputes the signature over `@raw_body`. The application-level handler then receives `WebhookMetadata` claiming to be for the victim shop, resulting in cross-tenant data confusion — e.g., triggering `app/uninstalled`, `shop/redact`, or other tenant-scoped side effects (session/data deletion, cache invalidation, state changes) attributed to a shop the attacker does not control. Similarly, swapping the `topic` header can route a validly-signed body to the wrong handler, causing it to be parsed/acted on under semantics it wasn't intended for.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the app on an attacker-controlled shop to obtain one genuine signed webhook, and (2) the ability to POST directly to the app's webhook endpoint (which is inherently public/unauthenticated by design, since Shopify's own delivery is just an HTTP POST with headers). No access to `api_secret_key`, tokens, or Shopify infrastructure is needed — only replay of previously-observed legitimate traffic with modified headers. This is realistic for any app that exposes its webhook endpoint on the public internet, which is the standard deployment model.

### Recommendation
Bind `shop` and `topic` into the signed material verified before they are trusted, or otherwise cryptographically/independently corroborate the shop domain (e.g., cross-check `request.shop` against a known/allow-listed set of installed shop domains before dispatching) rather than trusting header values that share no integrity relationship with the HMAC-covered body. At minimum, document that `Registry.process` callers must independently verify `shop`/`topic` correspond to an expected, currently-installed tenant before acting on `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, triggering Shopify to deliver a legitimate webhook, e.g. `app/uninstalled`, with body `B` and header `shopify-hmac-sha256: H` (valid for `B` under the app's secret) and `shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends this exact request to the app's public webhook endpoint, but replaces the header:
   `shopify-shop-domain: victim.myshopify.com`
   (and, optionally, `shopify-topic: shop/redact` if replaying a body compatible with that handler).
3. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim.myshopify.com", ...})` and calls `Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only — unaffected by the header change — and returns `true`. [4](#0-3) 
5. The registered handler for the (possibly attacker-chosen) topic is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, causing the app to act as though the event originated from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
