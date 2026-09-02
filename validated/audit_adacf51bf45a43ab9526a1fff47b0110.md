### Title
Webhook `shop`/`topic`/`webhook_id`/`api_version` fields are not covered by the HMAC signature, allowing cross-tenant data injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC only over `request.to_signable_string` (the raw body). All the other attacker-controlled request metadata — `shop`, `topic`, `webhook_id`, `api_version` — are taken straight from HTTP headers and are never included in the signed material, yet they are trusted and forwarded to the host application's webhook handler as the tenant/routing identity.

### Finding Description
`Registry.process` is the analog of the reported `withdrawBySnapshot()` flaw: a value used to establish "which tenant/state this data belongs to" is accepted without being bound to the cryptographically verified payload.

- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all read directly from HTTP headers, independent of the signed body: [2](#0-1) 
- `HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it against the `hmac` field — it never touches `shop`, `topic`, `webhook_id`, or `api_version`: [3](#0-2) 
- `Registry.process` trusts the HMAC check alone, then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` and passes it to the registered handler: [4](#0-3) 

The binding that should hold is:
`HMAC(raw_body) valid` ⇒ `(shop, topic, webhook_id, api_version) authentic`

But the actual binding enforced is only:
`HMAC(raw_body) valid` ⇒ `raw_body authentic`

Because `shop` (and the other headers) are outside the signed scope, anyone who obtains one valid `(raw_body, hmac)` pair for any shop (e.g., by receiving a legitimate webhook for their own low-privilege/trial store, or by capturing one in transit/logs) can resubmit that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and `X-Shopify-Topic` / `X-Shopify-Webhook-Id`) header. `HmacValidator.validate` will still report success because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop as the origin of that (unrelated) payload.

### Impact Explanation
This crosses a tenant boundary: the host application's webhook handler receives data it believes is scoped to `shop = X` (used for keying database writes, GDPR redaction handling, order/customer state updates, etc.) when in fact the HMAC only proves the body came from *some* Shopify webhook sender, not from shop `X` specifically. This can cause cross-tenant data corruption or spoofed lifecycle events (e.g., spoofing `shop/redact`, `customers/redact`, or `customers/data_request` mandatory webhooks against a victim shop) — matching the "cross-tenant access" Critical category.

### Likelihood Explanation
Exploitation requires possession of one genuine `(raw_body, hmac)` pair, which is far weaker than requiring the app's `client_secret`: it can be obtained by controlling any store that has installed the app (even a free/dev store), or by observing a webhook payload in transit/logs, since `hmac` is computed only from the body and the shared secret — never from `shop`. The attacker never needs the `api_secret_key` itself, only a previously-issued valid body/signature pair, then replays it with forged routing headers.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material used for verification (or otherwise cryptographically bind them to the verified body), mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes all relevant fields (`code`, `host`, `shop`, `state`, `timestamp`) in its signable string: [5](#0-4) 
At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop/topic headers so `HmacValidator` actually authenticates the tenant identity, not just the raw body.

### Proof of Concept
1. Attacker installs the app on their own Shopify dev store (`attacker.myshopify.com`) and triggers a real webhook (e.g., `orders/create`), capturing the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - Same `raw_body` and same `X-Shopify-Hmac-Sha256` value (unchanged — still valid because HMAC only covers the body).
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged).
   - `X-Shopify-Topic` optionally changed to a sensitive topic (e.g., `shop/redact`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body` (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the signed body has nothing to do with that shop — a cross-tenant confusion the host app cannot detect since the gem presents it as authenticated.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
