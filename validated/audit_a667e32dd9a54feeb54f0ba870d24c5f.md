The library's webhook verification signs only the request body, not the identifying headers, which breaks the tenant binding.Confirmed: the `Registry.process` flow validates the webhook solely via `Utils::HmacValidator.validate(request)`, which delegates to `request.to_signable_string` — the raw body only — while `request.shop`, `topic`, `webhook_id`, and `api_version` come from unsigned HTTP headers and are passed straight into the handler.This confirms the analog is fully rooted in library code: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled unauthenticated from HTTP headers [2](#0-1) , and `Registry.process` forwards these header-derived values straight to the handler after only checking the body HMAC [3](#0-2) .

### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body [4](#0-3) . The tenant-identifying field `shop` (as well as `topic`, `webhook_id`, `api_version`) is read from unsigned HTTP headers via `Request#shop`/`shopify_header` [5](#0-4)  and is never included in the HMAC-signed content, which is limited to `@raw_body` [1](#0-0) . This breaks the intended identity binding: `shop (HMAC-verified) == shop (used to attribute/process the event)`.

### Finding Description
`HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only the raw body [1](#0-0) , and compares it against the `hmac-sha256` header using `OpenSSL.secure_compare` [6](#0-5) . Crucially, this HMAC is computed with the app's single, static `api_secret_key`, which is identical across every shop that installs the app — it is not shop-specific. The `shop` value that `Registry.process` hands to the app's `handler.handle` callback (`WebhookMetadata.new(... shop: request.shop ...)`) comes from the `x-shopify-shop-domain`/`shopify-shop-domain` header [7](#0-6)  and is never part of the signed bytes.

Because the app secret is shared across all shops, any user who installs the app on their own store (a legitimate, unprivileged action) receives genuine webhook deliveries with a valid HMAC for a given raw body. That attacker can then replay the exact same `raw_body` + `hmac-sha256` value to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header (e.g., a victim shop). `HmacValidator.validate` will still pass, because it only checks the body bytes against the shared secret — it never binds the signature to the shop that is claimed in the headers. The handler consequently processes attacker-controlled data as if it originated from the victim shop.

### Impact Explanation
This is a cross-tenant integrity/spoofing issue: an app built on this gem cannot distinguish "this event body was validly signed by Shopify for the shop named in headers" from "this event body was validly signed by Shopify for the attacker's own shop, replayed with a forged shop-domain header." Depending on how the host app keys its data/state off `WebhookMetadata#shop`, this enables cross-tenant data corruption or disclosure (e.g., writing attacker-supplied order/customer data into another merchant's records, or triggering mandatory-compliance handlers like `customers/redact` against an arbitrary shop). This matches the "Critical - cross-tenant access" category, since the tenant boundary (`shop`) is not cryptographically bound to the authenticated payload.

### Likelihood Explanation
Likelihood is high for any integrator who trusts `WebhookMetadata#shop` as an authenticated tenant identifier (this is the gem's documented usage pattern) since:
- The attacker needs no privileged credentials — simply installing the app on their own (attacker-controlled) development/trial store is sufficient to obtain validly-HMAC'd payloads signed with the app's shared secret.
- No brute-forcing of the HMAC is required; the attacker owns a legitimate signed sample and only needs to replay it with modified headers to the same public webhook endpoint.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable content used for `to_signable_string`, or otherwise cryptographically bind the `shop` claim to the payload before trusting it. At minimum, document (and, better, enforce in this gem) that host applications must independently verify that the shop named in the webhook belongs to a shop with an active, known session/installation for this app before acting on the payload, rather than trusting the header value implicitly once HMAC-over-body passes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, causing Shopify to send a legitimate webhook (e.g., `orders/create`) to the app's public endpoint with a valid `x-shopify-hmac-sha256` for some `raw_body`.
2. Attacker captures `raw_body` and its valid `hmac-sha256` value.
3. Attacker POSTs the same `raw_body` and `hmac-sha256` to the app's webhook endpoint again, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` [4](#0-3) , which succeeds because it only checks `raw_body` against the shared app secret.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [7](#0-6) , causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
