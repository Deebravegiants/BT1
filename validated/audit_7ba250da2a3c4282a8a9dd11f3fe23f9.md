I have sufficient evidence to write up the finding on the webhook HMAC scope gap.### Title
Webhook shop-domain identity spoofing due to HMAC coverage excluding the tenant identity header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then hands the *unauthenticated* `shop-domain` header straight to the app's handler as the tenant identity. The equality the code implicitly relies on — "the shop the handler acts for" == "the shop cryptographically bound to this payload" — does not hold, because the HMAC never covers the `shop` field.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `verifiable_query.to_signable_string`, i.e. only the body bytes: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers with no cryptographic binding to the signature: [3](#0-2) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop` taken from that unauthenticated header, passing it straight to the host app's handler as the trusted tenant identifier: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no validation against the signature or against any known/registered shop: [5](#0-4) 

This is structurally identical to the reported bug class: a field (`shop`) is acted upon by downstream logic but is not covered by the HMAC that is supposed to authenticate the whole request. Since `api_secret_key` is shared across every shop that has the same app installed, any shop that has installed the app can capture one of its own genuine webhook deliveries (valid body + valid HMAC, since the secret is app-wide, not per-shop), and then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a different, victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is untouched), and `Registry.process` will invoke the handler with `data.shop` set to the attacker-chosen victim domain, causing the host application to attribute/act on that webhook payload as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant isolation the webhook mechanism is supposed to guarantee: a merchant/attacker who is merely a legitimate (unprivileged) installer of the app on their own shop — no stolen credentials, no access token, no `api_secret_key` needed — can make the app process attacker-controlled webhook data under another tenant's identity. Depending on how the host app uses `WebhookMetadata.shop` (e.g., to select which tenant's session/store/data to update, trigger redact/compliance flows, or route business logic), this enables cross-tenant data injection/corruption, which maps to the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged onboarding flow) and be able to POST arbitrary HTTP headers to the app's webhook endpoint (trivial, since it's a public HTTP endpoint). No secret material needs to be stolen — the attacker only needs one genuine webhook delivery from Shopify to their own shop to obtain a valid `(body, hmac)` pair they can replay with a forged shop header.

### Recommendation
Bind the shop identity to the authenticated payload instead of trusting the unauthenticated header value in isolation:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the signable string that is HMAC-verified, if a signing scheme change is possible, or
- Cross-check `request.shop` against session/registration state maintained by the host app before dispatch, and reject/flag webhooks whose header-declared shop does not match any shop the app expects for that HMAC/body pairing, or
- At minimum, document prominently that `WebhookMetadata.shop` is unauthenticated relative to the HMAC and must not be trusted as a tenant boundary without additional server-side verification (e.g., comparing against a known list of installed shops before applying the payload).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (normal app install, no privileged access).
2. Shopify delivers a genuine webhook to the app's endpoint:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of raw body B, computed with the app's shared api_secret_key>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   body: B
   ```
3. Attacker captures this exact `(B, hmac)` pair (e.g., from network logs of their own store, since `raw_body` can be a payload attacker controls indirectly, e.g. by triggering an action on their own store that produces a predictable body).
4. Attacker replays the request to the app's webhook endpoint, keeping body `B` and the HMAC header identical, but changing:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it only checks `B` against the HMAC: [6](#0-5) 
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host app to process attacker-supplied data as if it belongs to `victim-shop`.

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
