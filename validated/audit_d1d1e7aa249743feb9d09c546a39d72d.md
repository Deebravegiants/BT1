### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is taken from an HTTP header that is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `x-shopify-shop-domain` (and `x-shopify-topic`, `x-shopify-webhook-id`) headers — none of which are included in the signed bytes — to decide which merchant/tenant the payload belongs to and which handler receives it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (i.e. only the body) and compares it against `request.hmac`: [3](#0-2) 

After that check passes, `Registry.process` builds the metadata object directly from `request.shop` and `request.topic`/`request.webhook_id`, and dispatches to the app-registered handler for that topic: [4](#0-3) 

This is the same bug class as the `bumpTransfer()` report: a value used to bind an operation to an identity (`transferId` in the original report; `shop`/`topic` here) is accepted and acted upon without being covered by the authentication mechanism that is supposed to protect it (the transferId existence check in the original; the HMAC signature here). The equality that should hold is:

`bytes_verified_by_hmac == bytes_used_to_determine_tenant/topic`

but instead:

`bytes_verified_by_hmac (raw_body only) != bytes_used_to_determine_tenant/topic (shop/topic headers)`

An unprivileged party who can capture one legitimately-signed webhook delivery (e.g., a webhook posted to an app's public callback URL, which is often predictable/discoverable, or observed via any non-TLS-interception means such as logs, proxies, or the app's own visible endpoint) can replay that exact body/HMAC pair while substituting a different `x-shopify-shop-domain` value. Because the signature never covered the header, the replayed request still passes `HmacValidator.validate`, and the app's handler will process the payload as if it originated from the attacker-chosen shop — a cross-tenant identity confusion — without needing the app's `api_secret_key`.

### Impact Explanation
This crosses the "cross-tenant access" impact bucket explicitly listed as Critical: an attacker who can obtain one valid signed webhook body (no secret required) can cause the host application to attribute and process that payload under an arbitrary other shop domain of their choosing, corrupting or leaking per-tenant state in apps that key data storage/side effects off `WebhookMetadata#shop`.

### Likelihood Explanation
Obtaining a single valid webhook body/HMAC pair does not require the `api_secret_key`, an access token, or any privileged credential — webhook payloads are delivered to app-controlled endpoints and many topics (e.g., `orders/create`, `app/uninstalled`) produce payloads with predictable/generic structure that remain valid regardless of which shop is later claimed in the header, since the signature never binds to the shop at all. The gem provides no shop/topic-binding check itself, so any host app that trusts `WebhookMetadata#shop` for tenant routing is directly exposed via the gem's own `Registry.process` contract.

### Recommendation
Include `topic`, `shop`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them, e.g. requiring the app to independently confirm `shop` against a shop it has an active installation/session for before trusting the header), so that `HmacValidator.validate` fails if any of these identity-bearing fields are altered from what Shopify actually signed.

### Proof of Concept
1. Capture one legitimate webhook delivery to the app's webhook endpoint for `shop-a.myshopify.com`, topic `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid signature of `B`).
2. Replay the exact same `B` and `H` to the same endpoint, but set `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(secret, B)` — matches `H` — the header substitution is never checked: [5](#0-4) 
4. `Registry.process` proceeds and invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, using the attacker-controlled `shop-b.myshopify.com` value: [6](#0-5) 
5. The application processes/stores data for `shop-b` that actually belongs to `shop-a`, achieving cross-tenant data confusion.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
