## Title
Webhook `shop-domain` header is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the shop identity (`shop-domain` header) that the webhook handler trusts for tenant attribution is read separately from an unauthenticated header. Any actor who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared secret — which happens for every shop installed on a multi-tenant app, since all shops share the same `Context.api_secret_key` — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header. The gem's `Registry.process` validates only the HMAC over the body and then unconditionally trusts the attacker-controlled `shop` header for dispatch, breaking the binding `hmac_verified_bytes == identity_bytes_trusted`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is pulled straight from the `shop-domain` HTTP header with no cryptographic linkage to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `to_signable_string` (i.e., the body) and compares against the `hmac` header — it never touches `shop`: [3](#0-2) 

After that check passes, `process` immediately forwards `request.shop` — the unauthenticated header value — to the handler as the tenant identifier for the delivered body: [4](#0-3) 

Because `Context.api_secret_key` is a single app-wide secret shared by every shop that installs the app (it is not per-shop), any merchant who installs the app can trigger a genuine webhook delivery to their own endpoint, capture the valid `(raw_body, x-shopify-hmac-sha256)` pair Shopify sent them, and then POST that identical pair to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop that also uses the same app. `Utils::HmacValidator.validate` still succeeds (the body/HMAC pair is genuinely valid for the shared secret), and `Registry.process` hands the handler a `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-chosen `body`/`topic` content that was never actually generated for that shop.

### Impact Explanation
This breaks the equality that must hold for correct per-tenant processing: `shop_the_HMAC_was_computed_for == shop_attributed_to_the_data`. Only the raw body is authenticated; the shop identity used to route/store the webhook payload is not. An attacker who is merely an ordinary (or malicious) installer of the app — not a privileged party, no access token or `client_secret` required — can cause the host application to process attacker-influenced webhook data (topic + body) under another tenant's identity. Depending on how the host app persists webhook data (e.g., keyed by `shop`), this enables cross-tenant data injection/confusion, which maps to the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is moderate-to-high in any multi-tenant deployment of this gem: obtaining a valid `(body, hmac)` pair only requires installing the app on one's own store and triggering any subscribed webhook topic (e.g., updating a product), which is fully within the reach of an unprivileged, ordinary merchant/attacker. No secrets, tokens, or elevated access are needed — only the ability to replay an HTTP POST with a modified header to the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the verified signable string (or otherwise cryptographically tie the `shop-domain` header to the payload before trusting it), for example by including the shop domain in the HMAC computation, or by re-deriving/confirming the shop from a value that is itself authenticated (such as validating the webhook against the specific shop's registered secret/session rather than trusting the header verbatim). At minimum, document that `request.shop` must be cross-checked against an independently known/authorized shop list before being used to key any tenant-scoped write.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (both share the same `Context.api_secret_key`).
2. Attacker installs the app on `shop-a.myshopify.com` and triggers a webhook (e.g., `products/update`), capturing the real request: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` under the shared secret), per [5](#0-4) .
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` per [6](#0-5) .
5. `Registry.process` dispatches the handler with `shop: "shop-b.myshopify.com"` and the attacker-controlled `body`, per [4](#0-3) , causing the host app to record/act on data as if it came from `shop-b`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
