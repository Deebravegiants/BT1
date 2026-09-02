### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using the `shop` (and `topic`/`webhook_id`) values taken from unauthenticated HTTP headers. The equality the code implicitly assumes — "the shop that produced a validly-HMAC'd body == the shop asserted in the `shopify-shop-domain` header" — is never actually checked.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The header-derived `shop`, `topic`, `webhook_id`, and `api_version` accessors are populated straight from unauthenticated headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC (which covers the body) and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the dispatched `WebhookMetadata` used by the app's handler: [3](#0-2) 

`WebhookMetadata` carries `shop` as a plain, unauthenticated `String` field that the handler is expected to use as the tenant identifier: [4](#0-3) 

`HmacValidator.validate` computes/compares the signature purely from `verifiable_query.to_signable_string` (i.e., the body) and the app's single, shared `api_secret_key` — the same secret is valid for HMACs produced by *every* shop that installed the app, since it is an app-level (not per-shop) secret: [5](#0-4) 

Because the `shop-domain` header is excluded from the signed content, a party who can obtain one genuinely-signed webhook body (e.g., an unprivileged internet user who installs the same app on their own store — a fully self-service, unprivileged action) can replay that exact `raw_body` + valid `hmac` to the app's webhook endpoint while swapping only the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header value to name a victim shop. `HmacValidator.validate` will still pass because it only checks the body bytes against the shared secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

This is the same root-cause pattern flagged in the reference report: "a field acted on but not covered by the [authentication check]" — here the `shop` (tenant) identity field is acted upon by the handler dispatch but is not part of the HMAC-protected payload.

### Impact Explanation
This breaks the tenant isolation boundary the library is supposed to enforce for webhook delivery. An attacker who legitimately installs the app on their own shop (an unprivileged, self-service action requiring no leaked credentials) can forge webhook deliveries that are attributed to any other merchant's shop domain of their choosing. Any host application that uses `request.shop`/`data.shop` from `WebhookMetadata` to key data writes, trigger side effects, or make authorization decisions (which is the documented and expected usage pattern) can be made to process attacker-controlled body content under a victim shop's identity — i.e., cross-tenant data injection/corruption reachable purely from the HMAC-validated webhook entry point of this gem. This matches the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Likelihood is high for any app that has at least one other tenant (any merchant can install the app to obtain valid signed bodies) — the only prerequisite is installing the app on one's own store, which is an ordinary unprivileged action, not a privileged account, leaked secret, or social engineering. No knowledge of `api_secret_key` is required by the attacker; they merely reuse a body+signature pair Shopify legitimately produced for them and swap unsigned headers.

### Recommendation
Bind the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the signable content used by `HmacValidator`, or otherwise verify that they were produced together with the signed body (e.g., include them in `to_signable_string`, or cross-check `request.shop` against a shop known to be entitled to send the given `webhook_id`/topic before dispatching to the handler).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, unprivileged).
2. Attacker triggers an event whose webhook body content they control/observe (e.g., a `products/create` webhook), capturing the genuine `raw_body` and the corresponding `x-shopify-hmac-sha256` value that Shopify computed with the app's shared `api_secret_key`.
3. Attacker POSTs this exact `raw_body` and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and, if desired, a different `x-shopify-topic`/`x-shopify-webhook-id` consistent with what the handler expects).
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` (lines 12-31) succeeds because it only checks `raw_body` against the shared secret.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`, lines 188-200) dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: attacker-controlled-body, ...)` to the app's registered handler, which will process/store data as if it legitimately originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
